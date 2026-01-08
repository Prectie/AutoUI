from __future__ import annotations

from typing import Dict, Type, TypeVar

from Api.Base.api_client import ApiClient
from Api.Clients.task_client import TaskClient

ClientType = TypeVar("ClientType")


class ApiEntry:
    def __init__(self, client: ApiClient):
        self._client = client
        self._instances: Dict[str, object] = {}

    def _get(self, key: str, cls: Type[ClientType]) -> ClientType:
        if key not in self._instances:
            self._instances[key] = cls(self._client)
        return self._instances[key]  # type: ignore[return-value]

    @property
    def task(self) -> TaskClient:
        return self._get("task", TaskClient)
