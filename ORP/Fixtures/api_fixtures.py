import pytest

from Api.Base.api_client import ApiClient, ApiClientConfig
from Api.Config.env import get_api_base_url
from Api.entry import ApiEntry


@pytest.fixture(scope="session")
def api_client() -> ApiClient:
    config = ApiClientConfig(
        base_url=get_api_base_url(),
        headers={"Content-Type": "application/json;charset=UTF-8"},
    )
    return ApiClient(config)


@pytest.fixture(scope="session")
def api_entry(api_client: ApiClient) -> ApiEntry:
    return ApiEntry(api_client)
