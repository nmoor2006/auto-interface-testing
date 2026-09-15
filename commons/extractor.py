import jsonpath
import re
from typing import Any

def extract_by_jsonpath(data:str,expr:str)->Any:
    result=jsonpath.jsonpath(data,expr)#使用Jsonpath提取数据
    return result[0] if result else None

def extract_by_regex(text:str,pattern:str):
    match=re.search(pattern,text)
    return match.group(1) if match else None

