from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import yaml

from Utils.path_utils import PathTool


def _api_data_dir() -> Path:
    root = PathTool.project_root(__file__)
    data_dir = (root / "Api" / "Data").resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def load_json(filename: str) -> Dict[str, Any]:
    path = _api_data_dir() / filename
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_yaml(filename: str) -> List[Dict[str, Any]]:
    path = _api_data_dir() / filename
    with path.open("r", encoding="utf-8") as file:
        content = yaml.safe_load(file)
    if content is None:
        return []
    if isinstance(content, list):
        return content
    raise ValueError(f"YAML 文件 {filename} 必须返回列表结构")
