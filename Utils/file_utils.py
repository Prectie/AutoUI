import time
from pathlib import Path


def delete_test_download_file(filename: str, test_dir: str):
    """
    删除 Test/<角色脚本文件>/Downloads 下的指定文件

    Parameters:
    -----------
    filename : str
        要删除的文件名(含后缀)
    test_dir : str
        Tests 下的子目录名称
    """
    # 1.获取项目根目录路径
    project_root = Path(__file__).resolve().parent.parent
    # 2.拼接到每个角色下的Downloads路径
    download_dir = project_root / "Tests" / test_dir / "Downloads"

    # 3.拼接要删除的文件的路径
    file_path = download_dir / filename

    # 4.判断并删除
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
    else:
        raise FileNotFoundError(f"未找到文件{filename}")


def wait_for_download(download_dir: str, filename: str, timeout=20):
    """等待文件下载完毕, 返回下载的指定文件绝对路径

    Parameters:
    -----------
    download_dir:
        需要扫描的文件目录
    filename:
        要找的文件
    """
    end_time = time.time() + timeout
    download_path = Path(download_dir)

    while time.time() < end_time:
        for f in download_path.iterdir():
            if filename in f.name and not f.suffix in ((".crdownload", ".part")):
                return f
        # 每0.5秒检测一次(文件下载需要时间)
        time.sleep(0.5)
    logger.error(f"AssertionError: 文件{filename} 未在 {timeout}s 内下载完成")
    raise AssertionError(f"文件{filename} 未在 {timeout}s 内下载完成")