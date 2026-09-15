import logging
from typing import Any

logger=logging.getLogger(__name__)

def validate_response(response,expected_status:int=None,expected_json:dict=None,expected_text:str=None)->None:
    if expected_status is not None:
        assert response.status_code==expected_status,\
            f"状态码不匹配：期望{expected_status}"

    if expected_text is not None:
        import fnmatch
        if not fnmatch.fnmatch(response.text,expected_text):
            raise AssertionError(f"响应文本不匹配：期望:{expected_text}")

    if expected_json is not None:
        actual_json = response.json()
        _assert_json_subset(expected_json, actual_json)


def _assert_json_subset(expected:dict,actual:dict,path:str="$")->None:
    """递归断言expected是actual的子集"""
    for key,value in expected.items():
        current_path=f"{path}.{key}"
        if key not in actual:
            raise AssertionError(f"响应JSON缺少字段：{current_path}")

        """
        处理了两种复杂类型：字典（dict）和列表（list）
        """

        if isinstance(value, dict):
            if not isinstance(actual[key], dict):#如果预期值是字典，那么实际值也必须是字典，否则类型不匹配
                raise AssertionError(f"类型不匹配：{current_path} 应为对象")
            _assert_json_subset(value, actual[key], current_path)

        elif isinstance(value, list):
            if not isinstance(actual[key], list):
                raise AssertionError(f"类型不匹配：{current_path} 应为数组")

            if len(value)!=len(actual[key]):
                raise AssertionError(f"数组长度不匹配：{current_path}")

            for i,(exp_item,act_item) in enumerate(zip(value,actual[key])):
                if isinstance(exp_item,dict):
                    _assert_json_subset(exp_item,act_item,f"{current_path}[{i}]")
                else:
                    if exp_item!=act_item:
                        raise AssertionError(f"{current_path}[{i}] 期望 {exp_item}，实际 {act_item}")

        else:
            if value != actual[key]:
                raise AssertionError(f"值不匹配：{current_path} 期望 {value}，实际 {actual[key]}")