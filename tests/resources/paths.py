"""测试资源路径定义。

资源路径统一从本模块文件位置解析，避免依赖 pytest、IDE 或 CI 的当前工作目录。
资源按业务领域组织，使 Web、App 等不同测试平台可以共享同一份素材。
"""

from pathlib import Path


# 当前模块位于 tests/resources，向下拼接资源目录即可得到稳定的仓库内路径。
RESOURCE_ROOT = Path(__file__).resolve().parent

# 图片编辑器用例使用的标准图素材；原始文件需要由测试资源提交或准备流程提供。
EDITOR_STANDARD_IMAGE = (
    RESOURCE_ROOT / "images" / "editor" / "standard.jpg"
)
