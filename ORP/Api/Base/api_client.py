from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter, Retry

from Utils.log_utils import LoggerManager


logger = LoggerManager.get_logger("api_client")


@dataclass
class ApiClientConfig:
    base_url: str
    timeout: float = 10.0
    retries: int = 2
    backoff_factor: float = 0.2
    status_forcelist: tuple[int, ...] = (500, 502, 503, 504)
    headers: Dict[str, str] = field(default_factory=dict)


class ApiClient:
    def __init__(self, config: ApiClientConfig):
        self.config = config
        self.session = requests.Session()
        self._init_session()

    def _init_session(self) -> None:
        retry = Retry(
            total=self.config.retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=self.config.status_forcelist,
            allowed_methods={"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"},
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        if self.config.headers:
            self.session.headers.update(self.config.headers)

    def _build_url(self, path: str) -> str:
        base = self.config.base_url.rstrip("/")
        if path.startswith("/"):
            return f"{base}{path}"
        return f"{base}/{path}"

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> requests.Response:
        url = self._build_url(path)
        req_timeout = timeout if timeout is not None else self.config.timeout
        logger.info("HTTP %s %s", method.upper(), url)
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json,
            data=data,
            headers=headers,
            timeout=req_timeout,
        )
        logger.info("HTTP %s %s -> %s", method.upper(), url, response.status_code)
        return response

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        response = self.request(
            method,
            path,
            params=params,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
        )
        try:
            return response.json()
        except ValueError:
            logger.error("响应不是 JSON: %s", response.text)
            raise
