"""
AutoUI 运行时配置模块。

本模块负责读取 environments 目录下的 YAML 配置文件，
并将默认配置、站点配置、环境配置以及命令行参数合并为统一的 Settings 对象。

主要流程：
    1. load_profile() 读取指定环境配置文件；
    2. resolve_settings() 根据站点和环境选择目标配置；
    3. build_settings() 校验配置字段并创建 Settings 对象；
    4. pytest 插件可以通过 Settings 对象获取 base_url、viewport、locale 等配置。
"""

from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass(frozen=True)
class Viewport:
    """
    浏览器视口配置。

    属性：
        width: 浏览器视口宽度，单位为像素。
        height: 浏览器视口高度，单位为像素。

    frozen=True 表示对象创建后不能修改，可以避免测试运行过程中意外改变全局浏览器配置。
    """
    width: int
    height: int

@dataclass(frozen=True)
class Settings:
    """
    AutoUI 运行时的统一配置对象。

    该对象将分散在 YAML 文件中的配置集中到一个不可变对象中，
    供 pytest fixture、Playwright 浏览器配置以及页面对象使用。

    属性：
        base_url: 测试站点的基础 URL。
        viewport: 浏览器视口配置。
        locale: 浏览器使用的语言区域。
        timezone_id: 浏览器使用的时区。
    """
    base_url: str
    viewport: Viewport
    locale: str
    timezone_id: str

def load_profile(environment: str) -> dict:
    """
    加载指定名称的 YAML 配置文件。

    参数：
        environment:
            配置文件名称，不需要包含扩展名。
            例如传入 "defaults" 时，会加载：
            autoui/core/config/environments/defaults.yaml。

    返回：
        YAML 文件解析后的字典。
        如果 YAML 文件为空，则返回空字典。

    异常：
        如果配置文件不存在，抛出 ValueError；
        如果文件无法读取或 YAML 格式错误，则抛出对应的文件或 YAML 解析异常。
    """
    # 当前文件位于 autoui/core/config/settings.py
    # parent 指向 autoui/core/config 目录
    config_dir = Path(__file__).resolve().parent

    # 根据配置名称拼接 YAML 文件路径
    profile_path = config_dir / "environments" / f"{environment}.yaml"

    # 在读取文件前先检查文件是否存在，这样可以提供更明确的错误信息。
    if not profile_path.exists():
        raise ValueError(f"环境文件不存在, 请检查 environments 目录下是否存在 {environment}.yaml 文件")

    # 使用 UTF-8 编码读取配置文件
    with profile_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    # 当 YAML 文件为空时，yaml.safe_load() 会返回 None
    # 统一转换为空字典，避免调用方对 None 进行字典操作时出错
    return data or {}

def build_settings(profile: dict) -> Settings:
    """
    校验原始配置并构造 Settings 对象。

    参数：
        profile:
            已经合并后的配置字典。
            通常包含 base_url、viewport、locale 和 timezone_id 等字段。

    返回：
        校验完成后的不可变 Settings 对象。

    异常：
        如果缺少必填配置字段，抛出 ValueError。
        如果 viewport 内部缺少 width 或 height，会抛出对应的 KeyError。
    """
    # Settings 对象必须具备的顶层配置字段。
    required_fields = ("base_url", "viewport", "locale", "timezone_id")

    # 找出配置中缺失的必填字段。
    missing_fields = [
        field for field in required_fields if field not in profile
    ]

    # 配置不完整时立即终止，避免错误延迟到浏览器启动阶段才暴露
    if missing_fields:
        raise ValueError(
            f"配置缺少必填字段：{', '.join(missing_fields)}"
        )

    # viewport 是嵌套字典，需要进一步转换成 Viewport 对象
    viewport = profile["viewport"]

    # 将普通字典转换成类型明确且不可变的 Settings 对象
    return Settings(
        base_url=profile["base_url"],
        viewport=Viewport(
            width=viewport["width"],
            height=viewport["height"]
        ),
        locale=profile["locale"],
        timezone_id=profile["timezone_id"]
    )

def resolve_settings(
    cli_site: str | None=None,
    cli_env: str | None=None,
    cli_base_url: str | None=None,
):
    """
    根据默认配置、站点环境配置和命令行参数解析最终配置。

    参数：
        cli_site:
            命令行指定的站点名称。
            如果没有传入，则使用 defaults.yaml 中的 site。

        cli_env:
            命令行指定的环境名称。
            如果没有传入，则使用 defaults.yaml 中的 environment。

        cli_base_url:
            命令行指定的基础 URL。
            如果没有传入，则使用目标站点和环境中的 base_url。

    返回：
        解析并校验后的 Settings 对象。

    配置优先级：
        1. cli_base_url；
        2. targets.yaml 中对应站点和环境的配置；
        3. defaults.yaml 中的默认配置。

        对于 site 和 environment：
        命令行参数优先于 defaults.yaml 中的默认值。

    异常：
        如果指定的站点或环境不存在，抛出 ValueError；
        如果最终配置缺少必填字段，抛出 ValueError。
    """
    # 读取全局默认配置，例如默认站点和默认环境通常定义在 defaults.yaml 中。
    defaults = load_profile("defaults")

    # 读取不同站点和环境的具体配置。
    targets = load_profile("targets")

    # 命令行参数存在时优先使用命令行参数，否则回退到 defaults.yaml 中的默认值。
    site = cli_site or defaults["site"]
    environment = cli_env or defaults["environment"]

    try:
        # 根据站点和环境从 targets.yaml 中取出目标配置。
        target = targets[site][environment]
    except KeyError as e:
        raise ValueError(f"未知站点或环境：site={site!r}, environment={environment!r}") from e

    base_url = cli_base_url or target["base_url"]

    # 按优先级合并配置：
    # 1. defaults 提供基础默认值；
    # 2. target 覆盖 defaults 中相同的字段；
    # 3. base_url 使用最终解析出的 URL，优先级最高
    config = {
        **defaults,
        **target,
        "base_url": base_url
    }

    # 对合并后的配置进行字段校验，并转换成 Settings 对象
    return build_settings(config)

if __name__ == "__main__":

    setting = resolve_settings(
        cli_site="com",
        cli_env="beta",
        cli_base_url="www.xxx.com"
    )
    print(setting)
    print(setting.viewport.width)