# Python包、可选依赖与测试配置：逐行精讲

[精讲总目录](index.md) · [对应源码](../../pyproject.toml)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

把安装、包发现与测试收集规则显式化，保持词法核心可离线运行。

### 输入、输出与调用关系

pip/构建后端/pytest读取TOML，不是Python执行脚本。

### 运行与风险边界

核心 `python -m pip install -e .`；测试用 `python -m pip install -e ".[dev]"`。额外依赖按课安装，勿一键装所有大模型栈。

版本范围不是已测试精确快照；安装库不意味着已下载模型或获免费API权益。

## 完整源码

<!-- source: pyproject.toml -->
```toml
#: 构建后端告诉 pip 如何打包；setuptools>=68 是构建依赖，不是业务代码导入。
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

#: 项目身份与最低解释器版本；空 dependencies 保持核心离线标准库无额外运行依赖。
[project]
name = "evidencedesk"
version = "0.1.0"
description = "Evidence-first AI engineering guided course labs"
requires-python = ">=3.11"
dependencies = []

#: 按课选装 extras；允许范围不是实测锁，精确快照另见 requirements-tested.lock.txt。
[project.optional-dependencies]
dev = ["pytest>=8,<9"]
web = ["fastapi>=0.115,<1", "uvicorn>=0.30,<1", "httpx>=0.27,<1"]
vector = ["qdrant-client>=1.12,<2"]
ingest = ["pypdf>=5,<7", "tiktoken>=0.8,<1"]
llm = ["langchain-openai>=1,<2", "langchain-core>=1,<2"]
workflow = ["langgraph>=1,<2"]
advanced = ["deepagents>=0.3,<1", "mcp>=1,<2"]

#: src 布局让安装与包导入显式，避免项目根目录偶然掩盖安装问题。
[tool.setuptools.packages.find]
where = ["src"]

#: 默认仅收集 tests 中用例，不把教程示例当测试脚本执行。
[tool.pytest.ini_options]
testpaths = ["tests"]
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```toml
#: 构建后端告诉 pip 如何打包；setuptools>=68 是构建依赖，不是业务代码导入。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：构建后端告诉 pip 如何打包；setuptools>=68 是构建依赖，不是业务代码导入。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```toml
[build-system]
```

**语法与数据变化：** 声明构建系统表。

**为什么与边界：** 与业务运行依赖[project]分开。

<a id="L3"></a>
### 第 3 行

```toml
requires = ["setuptools>=68"]
```

**语法与数据变化：** 构建环境需要setuptools至少68。

**为什么与边界：** 不是业务代码import一个名为setuptools>=68的模块。

<a id="L4"></a>
### 第 4 行

```toml
build-backend = "setuptools.build_meta"
```

**语法与数据变化：** 指定PEP517构建后端入口。

**为什么与边界：** pip借它生成包元数据/可编辑安装，不是API服务启动命令。

<a id="L5"></a>
### 第 5 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L6"></a>
### 第 6 行

```toml
#: 项目身份与最低解释器版本；空 dependencies 保持核心离线标准库无额外运行依赖。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：项目身份与最低解释器版本；空 dependencies 保持核心离线标准库无额外运行依赖。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L7"></a>
### 第 7 行

```toml
[project]
```

**语法与数据变化：** 开始项目元数据表。

**为什么与边界：** 这里描述可安装分发包。

<a id="L8"></a>
### 第 8 行

```toml
name = "evidencedesk"
```

**语法与数据变化：** 分发名evidencedesk。

**为什么与边界：** 通常用于pip识别；导入包布局由src目录决定。

<a id="L9"></a>
### 第 9 行

```toml
version = "0.1.0"
```

**语法与数据变化：** 当前包版本0.1.0。

**为什么与边界：** 不等于语料正文版本或模型revision。

<a id="L10"></a>
### 第 10 行

```toml
description = "Evidence-first AI engineering guided course labs"
```

**语法与数据变化：** 人读项目简介。

**为什么与边界：** 不会自动生成业务功能。

<a id="L11"></a>
### 第 11 行

```toml
requires-python = ">=3.11"
```

**语法与数据变化：** 要求Python>=3.11。

**为什么与边界：** 旧解释器可能不支持用到语法/API，应换环境而非删除限制掩盖问题。

<a id="L12"></a>
### 第 12 行

```toml
dependencies = []
```

**语法与数据变化：** 核心额外运行依赖为空列表。

**为什么与边界：** 仅核心词法路径用标准库；API/模型例子仍需要extras。

<a id="L13"></a>
### 第 13 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L14"></a>
### 第 14 行

```toml
#: 按课选装 extras；允许范围不是实测锁，精确快照另见 requirements-tested.lock.txt。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：按课选装 extras；允许范围不是实测锁，精确快照另见 requirements-tested.lock.txt。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L15"></a>
### 第 15 行

```toml
[project.optional-dependencies]
```

**语法与数据变化：** 定义按功能安装的额外依赖组。

**为什么与边界：** `.[dev,web]`表示组合组，不是安装仓库所有可能库。

<a id="L16"></a>
### 第 16 行

```toml
dev = ["pytest>=8,<9"]
```

**语法与数据变化：** dev限定pytest8系列。

**为什么与边界：** 供测试使用，不能代替业务Web依赖。

<a id="L17"></a>
### 第 17 行

```toml
web = ["fastapi>=0.115,<1", "uvicorn>=0.30,<1", "httpx>=0.27,<1"]
```

**语法与数据变化：** web包括FastAPI路由、uvicorn服务、httpx客户端。

**为什么与边界：** 范围允许更新，不保证每个组合均经实际验收。

<a id="L18"></a>
### 第 18 行

```toml
vector = ["qdrant-client>=1.12,<2"]
```

**语法与数据变化：** vector安装Qdrant客户端1系列。

**为什么与边界：** 不包含自动下载embedding模型的授权。

<a id="L19"></a>
### 第 19 行

```toml
ingest = ["pypdf>=5,<7", "tiktoken>=0.8,<1"]
```

**语法与数据变化：** ingest安装pypdf与tiktoken。

**为什么与边界：** pypdf不做OCR，tiktoken首次编码表可能联网。

<a id="L20"></a>
### 第 20 行

```toml
llm = ["langchain-openai>=1,<2", "langchain-core>=1,<2"]
```

**语法与数据变化：** llm为LangChain OpenAI兼容适配与核心组件。

**为什么与边界：** 安装免费不等于运行模型免费，还需Key/端点/预算。

<a id="L21"></a>
### 第 21 行

```toml
workflow = ["langgraph>=1,<2"]
```

**语法与数据变化：** workflow安装LangGraph1系列。

**为什么与边界：** 内存checkpointer不自动持久化。

<a id="L22"></a>
### 第 22 行

```toml
advanced = ["deepagents>=0.3,<1", "mcp>=1,<2"]
```

**语法与数据变化：** advanced装deepagents与MCP。

**为什么与边界：** 它们能力不同，不能因为都在一组就开放Agent任意工具权限。

<a id="L23"></a>
### 第 23 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L24"></a>
### 第 24 行

```toml
#: src 布局让安装与包导入显式，避免项目根目录偶然掩盖安装问题。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：src 布局让安装与包导入显式，避免项目根目录偶然掩盖安装问题。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L25"></a>
### 第 25 行

```toml
[tool.setuptools.packages.find]
```

**语法与数据变化：** 配置setuptools的包发现。

**为什么与边界：** 让构建知道业务Python包在哪。

<a id="L26"></a>
### 第 26 行

```toml
where = ["src"]
```

**语法与数据变化：** 只在src内找可安装包。

**为什么与边界：** examples/tools通常从仓库根以模块运行，不自动等同分发包内容。

<a id="L27"></a>
### 第 27 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L28"></a>
### 第 28 行

```toml
#: 默认仅收集 tests 中用例，不把教程示例当测试脚本执行。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：默认仅收集 tests 中用例，不把教程示例当测试脚本执行。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L29"></a>
### 第 29 行

```toml
[tool.pytest.ini_options]
```

**语法与数据变化：** 开始pytest配置表。

**为什么与边界：** 仅影响测试发现与运行配置，不启动测试。

<a id="L30"></a>
### 第 30 行

```toml
testpaths = ["tests"]
```

**语法与数据变化：** 默认收集tests目录。

**为什么与边界：** 不会把所有在线examples自动执行，防无意外发或费用；新增测试仍需审查副作用。

## 跟一遍数据与验证边界

src布局要求安装或明确PYTHONPATH，不能因为终端cwd碰巧可导入就假定打包正确。

## 只练一个关键点（不是新的学习验收记录）

1. 运行 python -m pip show evidencedesk 和 python -m pytest --collect-only -q，观察安装路径与发现用例。
2. 比较[project]、extras和testpaths三处，暂不额外安装在线实验依赖。
3. **复盘：** 安装、导入、测试收集分别由哪处配置影响？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
