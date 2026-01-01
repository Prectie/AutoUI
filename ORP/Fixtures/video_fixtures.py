import shutil
import time

from datetime import date, timedelta, datetime
from pathlib import Path

import allure
import pytest

from Utils.log_utils import LoggerManager
from Utils.video_recorder import FFmpegRecorder


logger = LoggerManager.get_logger()


def pytest_addoption(parser):
    parser.addoption(
        "--video-keep-days",
        action="store",
        default=None,
        help="在 record_video 目录下保存录屏视频和日志, 并按天数留存/清理。CLI优先级高于配置文件"
    )
    parser.addini(
        "video_keep_days",
        default=2,
        help="按天数留存/清理录屏和日志, 默认保存最近2天的文件。CLI优先级高于配置文件"
    )

    # 控制是否启用录屏
    parser.addoption(
        "--ffmpeg-video",
        action="store",
        default="on",  # 默认开启录屏
        choices=("on", "off"),  # all=无论成功或失败, only-fail=仅失败, off=不 attach
        help="控制是否启用录屏, on 开启, off 关闭"
    )

    # 控制头部余量
    parser.addoption(
        "--video-lead",
        action="store",
        default=None,  # None表示不从命令行覆盖
        help="头部余量: 录制开始后空录指定的秒数, 需要在 ini/toml 配置文件中设置, 不设置默认为 1s"
    )
    parser.addini(
        "video_lead_seconds",
        default="1",  # 默认 1s
        help="头部余量: 录制开始后空录指定的秒数, 需要在 ini/toml 配置文件中设置, 不设置默认为 1s"
    )

    # 控制尾部余量
    parser.addoption(
        "--video-tail",
        action="store",
        default=None,
        help="尾部余量: 录制结束后空录指定的秒数, 需要在 ini/toml 配置文件中设置, 不设置默认为 2s"
    )
    parser.addini(
        "video_tail_seconds",
        default=2,
        help="尾部余量: 录制结束后空录指定的秒数, 需要在 ini/toml 配置文件中设置, 不设置默认为 2s"
    )

    # 控制是否把视频/日志 attach 到 Allure
    parser.addoption(
        "--video-allure",
        action="store",
        default="all",
        choices=("all", "only-fail", "off"),  # all=无论成功或失败, only-fail=仅失败, off=不 attach
        help="控制是否把视频/日志 attach 到 Allure, all=无论成功或失败均 attach, only-fail=仅失败时 attach, off=不 attach。默认 all"
    )

    # 控制是否 attach ffmpeg log
    parser.addoption(
        "--video-allure-attach-ffmpeg-log",
        action="store",
        default="on",
        choices=("on", "off"),
        help="控制是否 attach ffmpeg 日志文件, on 开启, off 关闭。默认 on"
    )


def _get_user_prop_last(item, key: str):
    value = None
    for k, v in item.user_properties:
        if k == key:
            value = v
    if value is None:
        return None
    return str(value)


def _has_user_prop(item, key):
    for k, _ in item.user_properties:
        if k == key:
            return True
    return False


def _attach_file_to_allure(file_path: str, name: str, attachment_type) -> None:
    """
    把文件作为附件 attach 到 Allure，并做健壮性检查。
    """
    p = Path(file_path)  # 转 Path 方便检查

    # 文件不存在就不 attach
    if not p.exists():
        logger.warning(f"[allure] file not exists, skip attach: {p}")  # 打日志
        return  # 返回

    # 空文件也不 attach（通常说明录制失败或尚未写入）
    if p.stat().st_size <= 0:
        logger.warning(f"[allure] file empty, skip attach: {p}")  # 打日志
        return  # 返回

    try:
        # attach.file 会把文件复制到 allure-results，因此本地后续清理不影响报告
        allure.attach.file(str(p), name=name, attachment_type=attachment_type)  # 真正 attach
        logger.info(f"[allure] attached: {name} -> {p}")  # 记录 attach 成功
    except Exception:
        logger.exception(f"[allure] attach failed: {p}")  # 打印异常堆栈


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    pytest 的标准 hook：每个测试会在 setup/call/teardown 三个阶段各调用一次。

    我们的策略：
    - 在 setup/call 阶段，如果失败，就用 user_properties 记录 test_failed=1（规范方式）
    - 在 teardown 阶段（此时录屏 fixture 已 stop、文件完整），按策略 attach 到 Allure
    """
    outcome = yield  # 先执行 pytest 原本的流程，拿到结果
    rep = outcome.get_result()  # 获取本阶段的 report（包含 passed/failed/skipped）

    # 读取用户配置：是否 attach 到 Allure
    mode = item.config.getoption("--video-allure")  # all/fail/off

    # 如果关闭 attach，直接返回
    if mode == "off":
        return  # 不做任何事情

    # 如果当前阶段是 setup 或 call，并且失败了，就记录一个标记到 user_properties
    if rep.when in ("setup", "call"):  # 只关心 setup/call 的失败
        if rep.failed:  # 如果本阶段失败
            # 用 user_properties 规范记录失败标记（hook 自己也能读到）
            item.user_properties.append(("test_failed", "1"))  # 标记：该用例失败过
        return  # setup/call 阶段不 attach，直接结束（等 teardown 再 attach）

    # 走到这里表示 rep.when == "teardown"
    # teardown 阶段 attach 的好处：录屏通常已经 stop，mp4 不容易损坏

    # 如果策略是 fail，则只有失败用例才 attach
    if mode == "only-fail":
        # 只要 user_properties 里存在 test_failed，就认为失败
        failed = _has_user_prop(item, "test_failed")  # 判断是否失败
        if not failed:
            return  # 成功用例不 attach

    # 从 user_properties 读取录屏路径（由录屏 fixture 写入）
    video_path = _get_user_prop_last(item, "record_video_path")  # mp4 路径
    log_path = _get_user_prop_last(item, "record_ffmpeg_log_path")  # log 路径

    # 如果没拿到视频路径，说明录屏 fixture 可能没执行或被关闭
    if not video_path:
        logger.info("[allure] record_video_path not found, skip attach")  # 打日志
        return  # 返回

    try:
        mp4_type = getattr(allure.attachment_type, "MP4", "video/mp4")  # 优先用常量，否则用 mime
        txt_type = getattr(allure.attachment_type, "TEXT", "text/plain")  # 文本类型
    except Exception:
        # 没有安装/启用 allure 插件时，import 会失败
        logger.info("[allure] allure not available, skip attach")  # 打日志
        return  # 返回

    # attach 视频（成功/失败都 attach 的核心就在这里）
    _attach_file_to_allure(video_path, "recording", mp4_type)  # 挂 mp4

    # 根据开关决定是否 attach ffmpeg 日志
    if item.config.getoption("--video-allure-attach-ffmpeg-log") == "on":
        # 只有 log_path 存在才尝试 attach
        if log_path:
            _attach_file_to_allure(log_path, "ffmpeg.log", txt_type)  # 挂 log


def get_tail_seconds(config) -> int:
    cli = config.getoption("--video-tail")
    if cli is not None:
        return int(cli)
    return int(config.getini("video_tail_seconds"))


def get_lead_seconds(config) -> int:
    cli = config.getoption("--video-lead")
    if cli is not None:
        return int(cli)
    return int(config.getini("video_lead_seconds"))


def get_keep_days(config) -> int:
    cli = config.getoption("--video-keep-days")
    if cli is not None:
        return int(cli)
    return int(config.getini("video_keep_days"))


def cleanup_old_record_video(root: Path, keep_days: int):
    """
      按日期清理目录
    :param root:
    :param keep_days:
    :return:
    """
    if keep_days <= 0:
        logger.warning(f"[video] keep_days={keep_days}, 异常数据, 跳过清理")
        return

    today = date.today()
    cutoff = today - timedelta(days=keep_days - 1)

    if not root.exists():
        return

    for day_dir in root.iterdir():
        if not day_dir.is_dir():
            continue

        try:
            day = datetime.strptime(day_dir.name, "%Y-%m-%d").date()
        except Exception:
            continue

        if day < cutoff:
            try:
                shutil.rmtree(day_dir, ignore_errors=False)
                logger.info(f"[video] 移除目录: {day_dir}")
            except Exception:
                logger.exception(f"[video] 移除目录失败: {day_dir}")


@pytest.fixture(scope="session")
def video_run_dirs(request):
    """
      每次运行时, 创建一套目录:
       artifacts/record_video
    :return:
    """
    # 项目根目录
    project_root = Path(__file__).resolve().parents[1]

    # 录屏根目录
    record_root = project_root / "record_video"

    keep_days = get_keep_days(request.config)
    logger.info(f"[video] keep_days={keep_days}")

    cleanup_old_record_video(record_root, keep_days)

    day = time.strftime("%Y-%m-%d")
    run_id = time.strftime("%H-%M-%S")

    run_root = record_root / day / run_id
    video_dir = run_root / "video"
    log_dir = run_root / "ffmpeg_log"

    video_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"[video] 运行根目录: {run_root}")
    return video_dir, log_dir


@pytest.fixture(autouse=True)
def auto_record_video(request, video_run_dirs):
    video_dir, log_dir = video_run_dirs

    lead_in_seconds = get_lead_seconds(request.config)  # 前置余量
    tail_seconds = get_tail_seconds(request.config)  # 后置余量
    r = FFmpegRecorder(video_dir=video_dir, log_dir=log_dir)

    name = request.node.nodeid

    video_path, log_path = r.start(name)

    request.node.user_properties.append(("record_video_path", str(video_path)))
    request.node.user_properties.append(("record_ffmpeg_log_path", str(log_path)))

    time.sleep(lead_in_seconds)
    try:
        yield
    finally:
        time.sleep(tail_seconds)
        r.stop()






