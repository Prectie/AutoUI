import os

import pytest

from Api.Utils.assertions import assert_status


@pytest.mark.api
def test_health_check(api_client):
    base_url = os.getenv("API_BASE_URL")
    if not base_url:
        pytest.skip("未设置 API_BASE_URL，跳过接口联调示例用例")
    response = api_client.request("GET", "/health")
    assert_status(response, 200)
