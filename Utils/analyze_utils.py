import itertools
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Any, Iterable

import yaml
from Utils.log_utils import LoggerManager
from Utils.path_utils import PathTool

logger = LoggerManager.get_logger()


# ================================ 定位 Data 目录及 yaml 文件路径 ================================
def _data_dir() -> Path:
    """ 获取本模块所在的根目录, 再拼接 Data/

    :return: Path 对象以便后续操作
    """
    root = PathTool.project_root(__file__)
    data = (root / "Data").resolve()
    if not data.is_dir():
        raise FileNotFoundError(f"未找到 Data 目录: {data}")
    return data


# 模块加载时只解析一次目录绝对路径
_DATA_DIR = _data_dir()


def _abs_data_path(filename: str) -> Path:
    """ 将路径规范为 "可用的绝对路径"

    :param filename: yaml 文件所在的相对路径或绝对路径
    :return: Path 对象以便后续操作

    使用示例:
    >> _abs_data_path("SystemAdminData/people.yaml")
    """
    p = Path(filename)
    return p.resolve() if p.is_absolute() else (_DATA_DIR / filename).resolve()


# ================================ YAML 读取与校验 ================================
@lru_cache(maxsize=256)
def _load_yaml_all(abs_path: str) -> List[Any]:
    """ 多文档 yaml 读取(带缓存)

    :param abs_path: yaml文件的绝对路径
    :return: list -> 每个 yaml 文件解析后的列表对象(通常为 dict)
    """
    ap = Path(abs_path)
    if not ap.exists():
        raise FileNotFoundError(f"数据文件不存在: {abs_path}")
    with ap.open("r", encoding="utf-8") as f:
        return list(yaml.safe_load_all(f))


def _read_yaml_list(abs_path: str, key: str) -> List[Dict[str, Any]]:
    """ 读取指定 key 对应的列表

    :param abs_path: yaml 文件绝对路径
    :param key: 要提取的数据段名称(yaml 顶层某个 key)
    :return: List[Dict[str, Any]] -> 用于后续合并的统一结构

    示例 YAML:
    ---
    tags:
      - smoke
      - regression
    people:
      - { name: "A", age: 18 }
      - { name: "B", age: 20 }

    示例:
    >> _read_yaml_list("abs/xxx.yaml", "tags")
    .. [{'tags': 'smoke'}, {'tags': 'regression'}]  兼容无字典情况
    >> _read_yaml_list("abs/xxx.yaml", "people")
    .. [{'name': "A", 'age': 18}, {'name': "B", 'age': 20}]
    """
    for doc in _load_yaml_all(abs_path):
        if isinstance(doc, dict) and key in doc:
            data = doc[key]
            if not isinstance(data, list):
                raise ValueError(f"{abs_path} 中 key='{key}' 应为 list, 实际: {type(data)}")
            out = []
            for item in data:
                out.append(item if isinstance(item, dict) else {key: item})
            return out
    raise KeyError(f"{abs_path} 中未找到 key='{key}'")


def _merge_dicts(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """ 浅合并多个字典(后者覆盖前者同名键)

    :param items: 列表里需要合并的字典
    :return: dict -> 合并后的字典
    """
    out = {}
    for d in items:
        if not isinstance(d, dict):
            raise TypeError(f"合并对象必须是 dict, 实际: {type(d)}")
        out.update(d)
    return out


# ================================ 统一入口(key -> 文件格式) ================================
def read_yaml_combine(
    key_files: Dict[str, str],
    *,
    mode: str = "cartesian"
) -> List[Dict[str, Any]]:
    """ 读取并合并测试数据(仅支持 "key -> 文件路径" 格式)

    :param key_files: dict, 形如:
                {
                    "account": "demo.yaml"
                    "role_msg": "Audited/people.yaml"
                }
                —— 支持不同 key 指向同一文件或不同文件
    :param mode:
            - 'cartesian' (默认, 做笛卡尔积全组合)
            - 'zip' (按位置一一对应, 要求各列表长度一致)
    :return: List[Dict[str, Any]] -> 合并后的用例数据
    """
    if not key_files:
        return []

    # 1.逐 key 读取列表
    data_lists = []
    for key, filename in key_files.items():
        ap = _abs_data_path(filename)
        lst = _read_yaml_list(str(ap), key)
        data_lists.append(lst)
        logger.debug(f"加载 {ap}: {key} -> {len(lst)} 条")

    # 2.合并
    if mode == "zip":
        # 每个 key 对应的长度
        lengths = {len(x) for x in data_lists}
        if len(lengths) != 1:
            raise ValueError(f"zip 合并要求每个 key 对应的列表等长, 实际长度集合: {sorted(lengths)}")
        return [_merge_dicts(list(row)) for row in zip(*data_lists)]

    if mode == "cartesian":
        return [_merge_dicts(list(prod)) for prod in itertools.product(*data_lists)]

    raise ValueError("mode 仅支持 'cartesian' 或 'zip'")


# ================================ 薄包装 ================================
def read_yaml_data(key: str, filename: str) -> List[Dict[str, Any]]:
    """ 读取单个 key 的列表(自动包装为 dict 元素 {key: value})

    :param key: 要提取的数据段名称(yaml 顶层某个 key)
    :param filename: Data 目录下的 yaml 文件相对路径
    :return: List[Dict[str, Any]] -> 单个 key 对应的用例数据
    """
    return _read_yaml_list(str(_abs_data_path(filename)), key)


def combine_same_file_key(
    keys: Iterable[str],
    filename: str,
    *,
    mode: str = "cartesian"
) -> List[Dict[str, Any]]:
    """ 同一个文件的多个 key 合并(默认笛卡尔积, 可选 "zip" )

    :param keys: 要提取的数据段名称(yaml 顶层某个 key)
    :param filename: Data 目录下的 yaml 文件相对路径
    :param mode:
            - 'cartesian' (默认, 做笛卡尔积全组合)
            - 'zip' (按位置一一对应, 要求各列表长度一致)
    :return: List[Dict[str, Any]] -> 合并后的用例数据

    示例:
    >> combine_same_file_key(["account", "role_msg"], "SystemAdminData/people.yaml", mode="zip")
    """
    return read_yaml_combine({k: filename for k in keys}, mode=mode)


if __name__ == "__main__":
    # 调试
    dic = {
        "account": "SystemAdminData/people_manage_data.yaml",
        "transfer_role": "SystemAdminData/people_manage_data.yaml",
        "advanced_query": "SystemAdminData/people_manage_data.yaml",
    }

    dic1 = {
        "drag_unit_order": "SystemAdminData/people_manage_data.yaml",
        "add_permission_role": "SystemAdminData/people_manage_data.yaml"
    }

    dic2 = {
        # ".6_test": "Common/accounts.yaml",
        "page": "Common/navigate_to_page.yaml",
        # "unknown_air_situation": "Case/app_portal_data.yaml"
    }

    dic3 = {
        "common_admin_account": "demo.yaml",
        "demo_e": "demo.yaml"
    }

    # print(combine_same_file_key(["common_admin_account", "demo_e"], "demo.yaml"))
    # print(read_yaml_data('auto_account', "Common/accounts.yaml"))
    # print(read_yaml_combine(dic2))

    # print(read_yaml_combine(dic3, mode='zip'))
    print(read_yaml_combine(dic2))
    # ap = Path("../Data/demo.yaml")
    # with ap.open("r", encoding="utf-8") as f:
    #     print(list(yaml.safe_load_all(f)))
