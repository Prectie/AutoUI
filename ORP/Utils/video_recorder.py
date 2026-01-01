import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from Utils.log_utils import LoggerManager

logger = LoggerManager.get_logger(__name__)


def safe_name(name: str) -> str:
    """
      把 pytest nodeid 等字符转换为安全文件名
    :param name: 需要处理的字符串
    :return: 将最后的 180 个字符返回, 限制长度
    """
    s = re.sub(r"[^a-zA-Z0-9_.-]", "_", name)
    return s[-180:]


def ensure_ffmpeg() -> str:
    """
      确认 ffmpeg 已安装且配置了环境变量
    :return: ffmpeg 的 bin 文件所在路径
    """
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError("找不到 FFmpeg, 请确认已安装并加入到系统环境变量。若仍然失败, 重启 IDE 再次尝试。")
    return ffmpeg_path


class FFmpegRecorder:
    def __init__(self, video_dir: Path, log_dir: Path, fps: int = 10):
        self.video_dir = Path(video_dir)
        self.log_dir = Path(log_dir)
        self.fps = fps

        self.proc: Optional[subprocess.Popen] = None
        self.video_path: Optional[Path] = None
        self.log_path: Optional[Path] = None
        self._log_fp = None

    def build_cmd(self, out_file: Path) -> list[str]:
        """
          生成用于 Windows 全屏录制的 ffmpeg 命令(无音频)
          输出为 mp4(h264) + yuv420p, 兼容 Windows 播放器

        :param out_file: 输出文件路径, 例如 record.mp4
        :return: 一组命令字符串
        """
        return [
            "ffmpeg",                     # 启动 ffmpeg 程序本体
            "-hide_banner",               # 打印少量编译信息
            "-y",                         # 覆盖同名输出文件
            "-f", "gdigrab",              # Windows 屏幕采集模块
            "-framerate", str(self.fps),  # 采集帧率
            "-i", "desktop",              # 输入源: 整个桌面
            "-an",                        # 不录音频
            "-c:v", "libx264",            # 输出视频编码: h264
            "-preset", "ultrafast",       # 编码速度优先
            "-crf", "28",                 # 画质/体积平衡
            "-pix_fmt", "yuv420p",        # Windows 播放器最兼容的像素格式
            "-movflags", "+faststart",    # 让 mp4 更容易被播放器/网页快速打开
            str(out_file),
        ]

    def start(self, name: str) -> tuple[Path, Path]:
        """
          开始录制视频
        :param name: 文件存储的目录名称
        :return: 视频和日志文件的存储路径
        """
        ffmpeg_path = ensure_ffmpeg()
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        base = safe_name(name)
        self.video_path = self.video_dir / f"{base}.mp4"
        self.log_path = self.log_dir / f"{base}.log"

        cmd = self.build_cmd(self.video_path)

        logger.info(f"[video] ffmpeg 安装路径: {ffmpeg_path}")
        logger.info(f"[video] 输出文件路径: {self.video_path}")
        logger.info(f"[video] 输出日志路径: {self.log_path}")

        self._log_fp = self.log_path.open("w", encoding="utf-8", errors="ignore", buffering=1)

        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=self._log_fp,
            stderr=self._log_fp,
            text=True,
        )

        return self.video_path, self.log_path

    def stop(self) -> None:
        """
          停止录制
        """
        if not self.proc:
            return

        try:
            if self.proc.stdin:
                self.proc.stdin.write("q\n")
                self.proc.stdin.flush()
        except Exception:
            logger.exception("[video] 尝试给 ffmpeg 发送 'q' 失败")

        try:
            self.proc.wait(timeout=10)
        except Exception:
            logger.exception("[video] ffmpeg 未及时退出, 尝试 kill()")
            try:
                self.proc.kill()
            except Exception:
                logger.exception("[video] kill ffmpeg 失败")

        try:
            if self._log_fp:
                self._log_fp.close()
        except Exception:
            logger.exception("[video] 关闭日志文件句柄失败")

        self.proc = None
        self._log_fp = None

