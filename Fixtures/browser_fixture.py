import pytest

from Config.settings import settings


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "base_url": settings.base_url,
        "viewport": {
            "width": settings.viewport.width,
            "height": settings.viewport.height,
        },
        "locale": settings.locale,
        "timezone_id": settings.timezone_id,
        "ignore_https_errors": True,
    }


