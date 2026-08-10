from pathlib import Path
import yaml
import pytest


def load_yaml(relative_path: str) -> dict:
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / relative_path

    with data_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)

DATA_FILES = {
    "demo": "tests/web/data/demo.yaml"
}

# 1. pytest_generate_tests(metafunc) 是什么意思
# 2. metafunc.fixturenames
# 3. domain 代表什么意思, scenario 代表什么意思
def pytest_generate_tests(metafunc):
    if "case" not in metafunc.fixturenames:
        return

    # 获取 marker.case_data
    marker = metafunc.definition.get_closest_marker("case_data")
    if marker is None:
        return

    # case_date("demo", "search_cases")
    domain, scenario = marker.args

    if domain not in DATA_FILES:
        raise ValueError(f"未知数据域：{domain}, 可用数据域：{list(DATA_FILES)}")

    data = load_yaml(DATA_FILES[domain])

    if scenario not in data:
        raise ValueError(f"未知数据场景：{scenario}, 可用场景：{list(data)}")

    cases = data[scenario]

    params = []

    for case in cases:
        tags = case.get("tags", [])
        marks = [getattr(pytest.mark, tag) for tag in tags]

        params.append(
            pytest.param(
                case,
                marks=marks,
                id=case.get("name", str(case))
            )
        )

    metafunc.parametrize("case", params)


if __name__ == "__main__":
    load_yaml("tests/web/data/demo.yaml")