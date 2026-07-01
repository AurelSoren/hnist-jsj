# hnist-jsj

> 教学平台接口学习示例。  
> 本项目仅用于 Python 网络请求、接口交互、加密参数构造与命令行程序结构的学习研究。

## 重要声明

本项目涉及第三方教学平台接口调用能力。请在阅读、下载、运行或二次开发前先完整阅读 [DISCLAIMER.md](./DISCLAIMER.md)。

你必须确保自己的使用行为符合所在学校、课程、平台服务条款、学术诚信规范以及当地法律法规。项目作者不鼓励、不支持、也不认可任何绕过教学要求、伪造学习成果、批量提交成绩、干扰平台正常运行或侵犯他人权益的行为。

## 项目简介

`zy.py` 是一个 Python 命令行脚本，主要演示：

- 使用 `requests` 调用 HTTP API；
- 使用 DES-CBC 构造登录参数；
- 维护访问令牌和基础请求参数；
- 获取课程、作业和分数信息；
- 通过交互式菜单组织命令行流程。

由于接口、业务规则和平台策略可能随时变化，本项目不保证任何功能长期可用。

## 目录结构

```text
.
├── zy.py
├── README.md
├── DISCLAIMER.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── requirements.txt
└── .gitignore
```

## 运行环境

推荐环境：

- 操作系统：Windows 10/11、macOS 或 Linux；
- Python：3.10 或更高版本；
- 包管理工具：`pip`；
- 网络环境：能够正常访问目标教学平台；
- 终端工具：PowerShell、Windows Terminal、Terminal、iTerm2 或其他命令行环境。

查看本机 Python 版本：

```bash
python --version
```

如果系统中同时安装了 Python 2 和 Python 3，macOS/Linux 可能需要使用：

```bash
python3 --version
```

## 依赖库

本项目依赖以下第三方库：

| 库名 | 用途 |
| --- | --- |
| `requests` | 发送 HTTP 请求，调用教学平台接口 |
| `pycryptodome` | 提供 `Crypto.Cipher.DES`，用于 DES 参数加密 |

依赖版本写在 [requirements.txt](./requirements.txt)：

```text
requests>=2.31.0
pycryptodome>=3.20.0
```

## 安装依赖

建议使用虚拟环境，避免污染系统 Python 环境。

### macOS / Linux

```bash
cd hnist-jsj
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows PowerShell

```powershell
cd hnist-jsj
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

如果 PowerShell 阻止激活虚拟环境，可在当前终端临时允许脚本执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 不使用虚拟环境

不推荐，但也可以直接安装到当前 Python 环境：

```bash
python -m pip install -r requirements.txt
```

macOS/Linux 如需指定 Python 3：

```bash
python3 -m pip install -r requirements.txt
```

## 验证安装

安装完成后可运行：

```bash
python -c "import requests; from Crypto.Cipher import DES; print('ok')"
```

如果输出 `ok`，说明依赖库已安装成功。

常见问题：

- 提示 `ModuleNotFoundError: No module named 'requests'`：说明 `requests` 没安装到当前正在使用的 Python 环境。
- 提示 `ModuleNotFoundError: No module named 'Crypto'`：请确认安装的是 `pycryptodome`，不是旧的 `crypto` 包。
- 提示 `pip` 不存在：可以尝试 `python -m ensurepip --upgrade` 后再安装依赖。

## 使用方式

交互式运行：

```bash
python zy.py
```

自动模式：

```bash
python zy.py --auto
```

自动模式会读取源码中的 `DEFAULT_XH`。公开仓库中不建议提交真实学号、姓名、班级、令牌、Cookie 或其他个人信息。建议在二次开发时改为从环境变量、命令行参数或本地配置文件读取。

## 配置说明

脚本内目前包含以下基础配置：

```python
BASE_URL = "http://www.ggjsj.cn"
DEFAULT_XH = "your_student_id"
```

开源前建议：

- 保持 `DEFAULT_XH` 为示例值，或改为从环境变量、命令行参数、本地配置文件读取；
- 不要提交任何真实账号信息；
- 不要提交运行日志、抓包文件、接口返回数据或包含个人信息的截图；
- 如需本地配置，使用未纳入版本控制的 `.env` 或 `config.local.json`。

## 合规使用建议

请只在以下场景使用本项目：

- 学习 Python HTTP 请求和异常处理；
- 研究命令行程序结构；
- 了解接口鉴权、请求体构造和响应解析的一般方法；
- 在得到明确授权的测试环境中做接口调试。

请不要在以下场景使用本项目：

- 未经授权访问、测试或调用第三方平台；
- 代替本人完成课程、作业、考试或考核；
- 伪造、篡改或批量提交学习记录与成绩；
- 对平台进行高频请求、压力测试或其他可能影响服务稳定性的操作；
- 收集、保存、传播他人的账号、成绩、课程等个人信息。

## 开源前检查清单

- [ ] 已删除真实学号、姓名、班级、学校、令牌、Cookie 等个人信息；
- [ ] 已确认代码中没有私钥、密码、接口凭证或抓包数据；
- [ ] 已阅读并保留 `DISCLAIMER.md`；
- [ ] 已选择并保留合适的开源许可证；
- [ ] 已确认公开代码不会违反学校、课程或平台规则；
- [ ] 已确认 README 不鼓励违规使用。

## 许可证

本项目以 MIT License 开源，详见 [LICENSE](./LICENSE)。

请注意：开源许可证只授予代码层面的使用、复制、修改和分发权利，不代表授权你访问任何第三方平台，也不免除你遵守法律法规、平台条款和学校规定的责任。
