"""
pytest 测试数据插件。

本模块负责从 YAML 文件加载测试数据，并通过 pytest_generate_tests()
在测试收集阶段自动生成参数化测试用例。

测试函数只需要声明 case 参数，并使用：

    @pytest.mark.case_data("demo", "search_cases")

即可将 YAML 中的测试数据注入到 case 参数中。
"""

from pathlib import Path
import yaml
import pytest

# 数据域名称与 YAML 文件路径的映射关系。
# 测试用例通过 domain 找到对应的数据文件。
DATA_FILES = {
    "demo": "tests/web/data/demo.yaml"
}

def load_yaml(relative_path: str) -> dict:
    """
    根据相对项目根目录的路径加载 YAML 文件。

    参数：
        relative_path: 相对于项目根目录的 YAML 文件路径。

    返回：
        YAML 文件解析后的字典对象。

    异常：
        如果文件不存在、编码错误或 YAML 格式不正确，会抛出对应的文件或解析异常。
    """
    # parents[2] 指向项目根目录 AutoUI。
    project_root = Path(__file__).resolve().parents[2]

    # 将项目根目录与传入的相对路径拼接成完整文件路径。
    data_path = project_root / relative_path

    # 使用 UTF-8 编码打开 YAML 文件，并安全解析其中的数据。
    with data_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def pytest_generate_tests(metafunc):
    """
    pytest 的参数化测试生成 hook。

    当测试函数同时满足以下条件时，该函数会自动生成参数化用例：

    1. 测试函数声明了名为 case 的 fixture 参数；
    2. 测试函数使用了 @pytest.mark.case_data(domain, scenario)；
    3. 指定的数据域和测试场景存在于对应的 YAML 文件中。

    参数：
        metafunc: pytest 提供的 Metafunc 对象，包含当前测试函数、
                  fixture 名称、marker 和参数化配置等信息。

    处理流程：
        YAML 测试数据 -> 读取场景 -> 生成 pytest.param ->
        调用 metafunc.parametrize() 注入 case 参数。
    """
    # metafunc.fixturenames 保存当前测试函数声明的 fixture 参数名称，也就是测试函数需要的参数
    # 如果测试函数不需要 case，就不需要进行数据驱动参数化
    if "case" not in metafunc.fixturenames:
        return

    # 获取当前测试函数上距离最近的 case_data marker
    # 例如：@pytest.mark.case_data("demo", "search_cases")
    marker = metafunc.definition.get_closest_marker("case_data")
    # 没有使用 case_data marker 时，不进行参数化。
    if marker is None:
        return

    # marker.args 保存 marker 的位置参数。
    # 这里约定第一个参数是数据域，第二个参数是测试场景
    domain, scenario = marker.args

    # 根据数据域查找对应的 YAML 文件。
    if domain not in DATA_FILES:
        raise ValueError(f"未知数据域：{domain}, 可用数据域：{list(DATA_FILES)}")

    # 加载指定数据域对应的 YAML 文件。
    data = load_yaml(DATA_FILES[domain])

    # 检查 YAML 中是否存在指定的测试场景。
    if scenario not in data:
        raise ValueError(f"未知数据场景：{scenario}, 可用场景：{list(data)}")

    # 获取当前场景下的全部测试用例
    # 每个 case 通常是一个字典，包含 name、tags、keyword 等字段
    cases = data[scenario]

    # 保存 pytest 参数化对象
    params = []

    for case in cases:
        # 读取当前用例的标签，没有 tags 时，默认使用空列表。
        tags = case.get("tags", [])

        # 将字符串标签转换为 pytest marker。
        # 例如 "smoke" 会转换为 pytest.mark.smoke。
        marks = [getattr(pytest.mark, tag) for tag in tags]

        # 将测试数据包装成 pytest 参数。
        # marks 用于给当前用例附加 marker；
        # id 用于生成更容易阅读的测试用例名称。
        params.append(
            pytest.param(
                case,
                marks=marks,
                id=case.get("name", str(case))
            )
        )

    # 将生成的参数注入测试函数的 case 参数。
    # 每个 case 都会被 pytest 作为一个独立测试用例执行。
    metafunc.parametrize("case", params)


if __name__ == "__main__":
    load_yaml("tests/web/data/demo.yaml")