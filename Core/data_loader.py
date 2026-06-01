from pathlib import Path
import yaml


def load_yaml(relative_path: str) -> dict:
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / relative_path

    with data_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)