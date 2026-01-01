import time
from pathlib import Path

import allure

import pytest

from Utils.log_utils import LoggerManager

logger = LoggerManager.get_logger()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """失败自动截图
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        try:
            driver = item.funcargs.get("driver") or item.funcargs.get("browser")
            if not driver:
                logger.error("失败截图功能未找到 driver")
                raise RuntimeError("未找到driver")
            if driver:
                timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
                png = driver.get_screenshot_as_png()

                filename = f"{item.name}_{timestamp}.png"

                allure.attach(
                    png,
                    name=f"{item.name}_{timestamp}",
                    attachment_type=allure.attachment_type.PNG
                )

                project_root = Path(__file__).parent.parent
                screenshots_dir = project_root / 'Screenshot'
                screenshots_dir.mkdir(exist_ok=True)
                file_path = screenshots_dir / filename
                with open(file_path, "wb") as f:
                    f.write(png)
        except Exception as e:
            logger.error(f"截图失败, 错误信息:\n{e}")
            raise e
