import pytest
import allure
from pathlib import Path
from commons.yaml_loader import read_yaml,load_env_config
from core.runner import Runner
from config.settings import settings

def get_all_yaml_cases():
    data_dir=settings.DATA_DIR
    return [str(p) for p in data_dir.glob("*.yaml")]

@pytest.mark.parametrize("yaml_file",get_all_yaml_cases())
def test_api(yaml_file):
    case_data=read_yaml(yaml_file)
    allure.dynamic.title(case_data.get("name",yaml_file))
    allure.dynamic.description(case_data.get("description",""))

    env_config=load_env_config(settings.ENV)
    runner=Runner(env_config)
    with allure.step("执行测试步骤"):
        runner.run(case_data["steps"])