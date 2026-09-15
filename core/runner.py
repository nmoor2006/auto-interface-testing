import logging
from typing import Any,Dict
from commons.requestor import send_request
from commons.validator import validate_response
from commons.extractor import extract_by_jsonpath, extract_by_regex
from commons.yaml_loader import load_env_config
from config.settings import settings

logger=logging.getLogger(__name__)

class Runner:
    def __init__(self,env_config:dict):
        self.env_config=env_config
        self.base_url=env_config.get("base_url","")
        self.timeout=env_config.get("timeout",10)
        self.context={}

    def run(self,steps:list):
        for step in steps:
            self._execute_step(step)

    def _execute_step(self,step:list):
        for keyword,params in step.items():
          if keyword=="request":
              self._do_request(params)

          elif keyword=="response":
              self._do_validate(params)

          elif keyword=="extract":
              self._do_extract(params)

          else:
              logger.warning(f"未知关键字：{keyword}")


    def _do_request(self,params:dict):
        params=self._replace_variables(params)

        method=params.pop("method","GET").upper()
        url=params.pop("url","")
        if url and not url.startswith("http"):
            # 规范化拼接：base_url 只放域名(可带目录前缀)，url 放以 / 开头的接口路径
            url=self.base_url.rstrip("/")+"/"+url.lstrip("/")
        elif not url:
            url=self.base_url

        params.setdefault("timeout",self.timeout)#处理超时

        resp=send_request(method,url,**params)
        self.context["response"]=resp
        logger.info(f"当前响应对象已存入 context['response']")

    def _do_validate(self,params:dict):
        resp=self.context.get("response")
        if resp is None:
            raise RuntimeError("没有可用响应对象，请先执行request步骤")

        params=self._replace_variables(params)

        validate_response(
            resp,
            expected_status=params.get("status_code"),
            expected_json=params.get("json"),
            expected_text=params.get("text")
        )

    def _do_extract(self,params:dict):
        resp=self.context.get("response")
        if resp is None:
            raise RuntimeError("没有可用的响应对象，请先执行 request 步骤")

        # 注意：提取逻辑必须放在循环体内，逐个变量提取；
        # 之前写在循环外，多个 extract 变量时只会提取最后一个
        for var_name,rule in params.items():
            if not isinstance(rule,dict):
                raise ValueError(f"extract 规则格式有误，应为字典：{var_name}={rule}")

            extract_type=rule.get("type","jsonpath")
            expr=rule.get("expr")

            if extract_type == "jsonpath":
                value = extract_by_jsonpath(resp.json(), expr)

            elif extract_type=="regex":
                value=extract_by_regex(resp.text,expr)

            else:
                raise ValueError(f"提取类型有误：{extract_type}")

            self.context[var_name]=value
            logger.info(f"提取变量：{var_name}={value}")

    def _replace_variables(self,data):
        """递归替换数据中的 ${var} 占位符"""
        if isinstance(data,dict):
            return {k:self._replace_variables(v) for k,v in data.items()}

        elif isinstance(data,list):
            return [self._replace_variables(item) for item in data]

        elif isinstance(data,str):
            import re
            pattern=r"\$\{([^}]+)\}"
            def replacer(match):
                var_name=match.group(1)
                return str(self.context.get(var_name,match.group(0)))
            return re.sub(pattern,replacer,data)

        else:
            return data







