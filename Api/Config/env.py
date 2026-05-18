from __future__ import annotations

import os


ENV_URLS = {
    "test": os.getenv("API_BASE_URL_TEST", "http://127.0.0.1:8180"),
    "prod": os.getenv("API_BASE_URL_PROD", "http://127.0.0.1:8180"),
}


def get_api_base_url() -> str:
    override = os.getenv("API_BASE_URL")
    if override:
        return override.rstrip("/")
    env_name = os.getenv("API_ENV", "test")
    return ENV_URLS.get(env_name, ENV_URLS["test"]).rstrip("/")
