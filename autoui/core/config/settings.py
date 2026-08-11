from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass(frozen=True)
class Viewport:
    width: int
    height: int

@dataclass(frozen=True)
class Settings:
    """
      配置集中在一个对象里
    """
    base_url: str
    viewport: Viewport
    locale: str
    timezone_id: str

def load_profile(environment: str) -> dict:
    config_dir = Path(__file__).resolve().parent
    profile_path = config_dir / "environments" / f"{environment}.yaml"

    if not profile_path.exists():
        raise ValueError(f"环境文件不存在, 请检查 environments 目录下是否存在 {environment}.yaml 文件")

    with profile_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data or {}

def build_settings(profile: dict) -> Settings:
    viewport = profile["viewport"]

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
    cli_site=None,
    cli_env=None,
    cli_base_url=None,
    env_vars=None
):
    env_vars = env_vars or {}

    defaults = load_profile("defaults")
    targets = load_profile("targets")

    site = cli_site or env_vars.get("AUTOUI_SITE") or defaults["site"]
    environment = cli_env or env_vars.get("AUTOUI_ENV") or defaults["environment"]

    try:
        target = targets[site][environment]
    except KeyError as e:
        raise ValueError(f"未知站点或环境：site={site!r}, environment={environment!r}") from e

    base_url = cli_base_url or env_vars.get("BASE_URL") or target["base_url"]

    config = {
        **defaults,
        **target,
        "base_url": base_url
    }

    return build_settings(config)




if __name__ == "__main__":

    setting = resolve_settings()
    print(setting)
    print(setting.viewport.width)