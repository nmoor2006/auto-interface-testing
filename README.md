# 接口自动化测试框架（pytest + YAML + Allure）

一个**数据驱动 + 关键字驱动**的接口自动化测试框架：测试用例用 YAML 描述（请求、断言、变量提取），
pytest 自动收集 `datas/` 下的 YAML 文件并参数化执行，Allure 生成可视化报告。
新增接口用例只需写 YAML，不用改代码。

---

## 一、特性

- **YAML 用例**：请求、断言、变量提取全部用 YAML 描述，零代码加用例
- **自动收集**：`datas/*.yaml` 自动参数化成 pytest 用例，一个文件即一条用例
- **关键字驱动**：`request` / `response` / `extract` 三个关键字覆盖"发请求 → 校验响应 → 提取变量"
- **多环境**：`config/env.yaml` 中按环境区分 `base_url`、`timeout`，用 `TEST_ENV` 环境变量切换
- **三种断言**：HTTP 状态码、JSON 子集递归断言、响应文本通配符断言
- **变量链路**：jsonpath / 正则提取响应数据为变量，通过 `${变量名}` 在后续请求参数、请求体、请求头、断言期望值中复用
- **日志完善**：控制台实时日志 + 文件日志（`logs/pytest.log`），均在 `pytest.ini` 统一配置
- **Allure 报告**：每条用例自动生成 Allure 结果，失败时附带完整请求/响应日志

---

## 二、目录结构

```
pytest project1/
├── commons/                     # 通用能力层
│   ├── extractor.py             # 数据提取：jsonpath、正则
│   ├── requestor.py             # requests 封装：统一日志与异常
│   ├── validator.py             # 响应断言：状态码 / JSON 子集 / 文本
│   └── yaml_loader.py           # YAML 读取、环境配置加载
├── config/
│   ├── env.yaml                 # 多环境配置（base_url、timeout）
│   └── settings.py              # 项目路径与环境变量（DATA_DIR/LOG_DIR/ENV）
├── core/
│   └── runner.py                # 用例执行引擎：关键字分发、变量替换、上下文管理
├── datas/                       # ★ YAML 测试用例（自动收集执行）
│   ├── article_detail.yaml
│   ├── home_index.yaml
│   ├── login.yaml
│   ├── login_wrong_pwd.yaml
│   └── search_by_category.yaml
├── testcases/
│   └── test_api.py              # pytest 入口：参数化 datas/*.yaml
├── logs/                        # 运行日志（已 gitignore）
├── report/                      # Allure 结果（已 gitignore）
├── conftest.py                  # 日志初始化
├── pytest.ini                   # pytest 配置（Allure、日志格式）
├── requirements.txt             # 依赖清单
└── README.md
```

---

## 三、环境要求与安装

- Python 3.10+（当前在 3.13.7 上验证通过）
- 查看 Allure 报告需要本机安装 [Allure 命令行](https://allurereport.org/docs/install/)（可选）

```bash
pip install -r requirements.txt
```

依赖：`pytest`、`requests`、`PyYAML`、`jsonpath`、`allure-pytest`。

---

## 四、快速开始

### 1. 配置被测环境

`config/env.yaml`：

```yaml
test:
  base_url: http://116.62.63.211   # 只写协议+域名，接口路径写在用例的 url 里
  timeout: 10
prod:
  base_url: https://api.example.com
  timeout: 20
```

### 2. 运行用例

```bash
pytest                              # 运行全部用例
pytest testcases/test_api.py -v     # 查看每条用例名
```

### 3. 切换环境

```bash
set TEST_ENV=prod && pytest         # Windows CMD
$env:TEST_ENV="prod"; pytest        # PowerShell
```

### 4. 查看 Allure 报告

```bash
pytest                                        # 结果写入 report/allure-results
allure serve report/allure-results            # 启动本地报告服务
```

---

## 五、用例编写说明

### 5.1 文件结构

```yaml
name: 用例名称
description: 用例说明
steps:
  - request: { ... }      # 发请求
  - response: { ... }     # 校验上一个请求的响应
  - extract: { ... }      # 从上个响应提取变量
```

### 5.2 request（请求）

| 字段 | 说明 |
| --- | --- |
| `method` | 请求方法，默认 `GET` |
| `url` | 以 `/` 开头的接口路径，与 `base_url` 拼接；也可直接写完整 `http` 地址 |
| `params` | URL 查询参数 |
| `json` | JSON 请求体 |
| `headers` | 请求头 |
| `timeout` | 超时时间，默认取环境配置 |

> 除 `method`、`url` 外的字段会原样透传给 `requests.request()`，因此 `data`、`cookies`、`files` 等同样可用。

### 5.3 response（断言）

| 字段 | 说明 |
| --- | --- |
| `status_code` | 期望 HTTP 状态码 |
| `json` | 期望的 JSON **子集**：递归比对，响应中多出来的字段会被忽略 |
| `text` | 期望响应文本，`fnmatch` 通配符匹配，如 `*"code":0*` |

### 5.4 extract（变量提取）

```yaml
- extract:
    token:
      type: jsonpath        # jsonpath（默认）或 regex
      expr: $.data.token
```

提取结果写入执行上下文，后续用 `${token}` 引用；一个 `extract` 步骤可同时提取多个变量。
**注意**：`request` 步骤之后必须紧跟 `response` 或 `extract`，它们读取的是"当前响应"。

### 5.5 完整示例：变量链路

```yaml
name: 商品分类-按分类搜索商品
steps:
  - request:
      method: GET
      url: /shop/api.php
      params: { s: goods/category }
  - response:
      status_code: 200
      json: { code: 0, msg: success }
  - extract:
      cate_id:   { type: jsonpath, expr: $.data.category[0].id }
      cate_name: { type: jsonpath, expr: $.data.category[0].name }
  - request:
      method: GET
      url: /shop/api.php
      params:
        s: search/index
        category_id: ${cate_id}          # 提取的变量作为请求参数
  - response:
      text: '*${cate_name}*'              # 提取的变量作为文本断言
      json:
        data:
          search_map_info:
            category:
              name: ${cate_name}          # 提取的变量作为 JSON 断言期望值
```

---

## 六、执行流程

```
pytest
  └── testcases/test_api.py            # 参数化 datas/*.yaml
        └── yaml_loader.read_yaml()    # 读取用例
              └── Runner.run(steps)    # 逐步骤执行
                    ├── request  → 变量替换 → 拼接 base_url → requestor.send_request() → 响应存入 context
                    ├── response → 取出 context['response'] → validator.validate_response()
                    └── extract  → extractor 提取 → 写入 context，供后续 ${变量} 使用
```

- `core/runner.py` 负责关键字分发与 `${变量}` 递归替换（支持 dict / list / str 嵌套结构）
- `commons/validator.py` 的 JSON 断言是**子集比较**，只校验用例中写到的字段
- 日志：控制台按 `pytest.ini` 的 `log_cli` 实时输出，同时写入 `logs/pytest.log`

---

## 七、内置用例清单

| 用例文件 | 覆盖场景 | 演示的框架能力 |
| --- | --- | --- |
| `home_index.yaml` | 商城首页、地区数据公开接口冒烟 | 状态码 / JSON 子集（空数组）/ text 通配符三种断言 |
| `search_by_category.yaml` | 商品分类 → 按分类搜索商品 | jsonpath 多变量提取 + `${变量}` 用于请求与断言 |
| `article_detail.yaml` | 文章详情 + 上/下一篇联动 | 多步骤串联、提取值跨请求校验 |
| `login.yaml` | 登录成功 + 未鉴权访问受限接口 | POST JSON 请求体、多步骤串联 |
| `login_wrong_pwd.yaml` | 密码错误、密码格式不合法 | 负向用例、错误码断言 |

> 内置用例针对演示环境 `http://116.62.63.211/shop/api.php`（公开学习用商城接口）。

---

## 八、已知限制与注意事项

1. **变量替换统一转字符串**：`${var}` 替换后是字符串。若提取到的是数字，用它断言数字字段会因 `3` 与 `'3'` 类型不同而失败——数字字段建议直接写字面量。
2. **数组断言是全量比较**：JSON 断言对数组按"长度 + 逐项"比较，因此长度会变化的非空数组不适合整体断言；可改用 `text` 通配符，或先用 jsonpath 提取再断言。
3. **断言是子集比较**：`json` 只校验用例写明的字段，响应多出的字段不影响结果；这可以避免接口新增字段导致用例大面积失败。
4. **演示环境接口契约**：该商城登录接口成功时只返回 `code:0/msg:登录成功`，不返回 `token`/`username`，且未登录访问 `user/index` 等一律返回 `code:-1000 非法访问`，所以内置用例只覆盖公开接口与失败分支。换成真实项目接口后，可按 5.5 的写法补充 token 提取与鉴权链路。
5. **演示账号**：用例中的账号密码是演示环境的公开测试账号，仅用于学习。

---

## 九、后续可扩展方向

- 新增关键字：`db`（数据库校验）、`script`（自定义脚本）、`sleep`（等待）
- 用例内数据驱动：一份 YAML 支持多组参数
- 前置/后置操作、用例间依赖与执行顺序控制
- CI 集成：GitHub Actions 执行 pytest 并归档 Allure 报告
- 断言增强：正则匹配、JSON Schema 校验、数组"包含"断言
- 与接口文档（Swagger/YApi）打通，自动生成 YAML 用例模板

---

## 十、说明

本仓库为开源学习项目，代码与用例仅供个人学习与交流使用，欢迎参考、交流与指正。
用例中的账号密码均为演示环境的公开测试账号，不涉及任何真实用户数据。
