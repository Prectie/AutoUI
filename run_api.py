import os
import time

import pytest


def run_tests():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    json_report_dir = f'./allure_json_report/api_{timestamp}'
    allure_report_dir = f'./allure_report/api_{timestamp}'

    os.makedirs(json_report_dir, exist_ok=True)
    os.makedirs(allure_report_dir, exist_ok=True)

    pytest_args = [
        "Tests/api",
        f'--alluredir={json_report_dir}',
    ]

    pytest.main(pytest_args)
    os.system(f"allure generate {json_report_dir} -o {allure_report_dir} --clean")
    os.system(f"allure serve {json_report_dir}")


if __name__ == "__main__":
    raise SystemExit(run_tests())
