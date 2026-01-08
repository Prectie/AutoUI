from __future__ import annotations

from typing import Any, Dict

from Api.Base.api_client import ApiClient


class TaskClient:
    def __init__(self, client: ApiClient):
        self.client = client

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.client.request_json("POST", "/ds/task/create", json=payload)

    def info(self, task_id: str) -> Dict[str, Any]:
        return self.client.request_json("POST", "/ds/task/info", json={"taskId": task_id})

    def stop(self, task_id: str) -> Dict[str, Any]:
        return self.client.request_json("POST", "/ds/task/stop", json={"taskId": task_id})

    def result(self, task_id: str) -> Dict[str, Any]:
        return self.client.request_json("POST", f"/ds/task/result?taskId={task_id}")
