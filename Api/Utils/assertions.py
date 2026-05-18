from __future__ import annotations

from typing import Any, Dict, Iterable


def assert_status(response, expected_status: int) -> None:
    actual = response.status_code
    assert actual == expected_status, f"状态码不匹配: 期望 {expected_status}, 实际 {actual}"


def assert_json_contains(actual: Dict[str, Any], expected: Dict[str, Any]) -> None:
    for key, value in expected.items():
        assert actual.get(key) == value, f"字段 {key} 不匹配: 期望 {value}, 实际 {actual.get(key)}"


def assert_json_path(data: Dict[str, Any], path: Iterable[str]) -> Any:
    cur: Any = data
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            raise AssertionError(f"路径不存在: {'.'.join(path)}")
        cur = cur[key]
    return cur
