import yaml
from pathlib import Path
from typing import Any

def read_yaml(file_path:str)->Any:
    with open(file_path,"r",encoding="utf-8") as f:
        return yaml.safe_load(f)#yaml文件经过 yaml.safe_load 解析后，得到的是一个 Python 字典

def load_env_config(env:str)->dict:
    """加载指定环境的配置"""
    env_file=Path(__file__).parent.parent/"config"/"env.yaml" #Path(__file__) 将文件路径__file__转换为 Path 对象
    all_env=read_yaml(str(env_file))
    return all_env.get(env,{}) #字典（dict）的核心操作——通过键（key）来获取对应的值（value），若无，则返回{}