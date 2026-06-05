from dataclasses import dataclass


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

settings = Settings(
    base_url="http://192.168.10.129:18080/",
    viewport=Viewport(width=1920, height=1080),
    locale="zh-CN",
    timezone_id="Asia/Shanghai",
)