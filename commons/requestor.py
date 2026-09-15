"""
封装 requests.request，统一处理超时、日志、异常。
"""

import requests
import logging

logger=logging.getLogger(__name__) #__name__ 是 Python 的一个内置变量，表示当前模块的名称

def send_request(method:str,url:str,**kwargs)->requests.Response:
    """发送HTTP请求，记录请求和响应简要信息"""
    logger.info(f"发送请求：{method.upper()} {url}")
    if 'params' in kwargs:
        logger.debug(f"查询参数：{kwargs['params']}")

    if 'json' in kwargs:
        logger.debug(f"JSON请求体：{kwargs['json']}")

    try:
        resp=requests.request(method,url,**kwargs)
        logger.info(f"响应状态码：{resp.status_code}")
        return resp

    except Exception as e:
        logger.info(f"异常：{e}")
        raise
