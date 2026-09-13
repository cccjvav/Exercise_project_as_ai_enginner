# 课程使用说明：先学当前课，不要一次安装全栈

## 0. 教材完成与学习进度是两回事

现在有 9 阶段、22 节完整小课。第一课保留细粒度逐行说明；后续每课都附完整代码、就近注释及行号对照，复杂的相邻语句按同一数据动作解释。参考代码都已给出，你不需要先独立写实现。

**当前进度：1A 已完成，1B 进行中；已完成空列表短路题、有效标题变式及正文非空对照实操。** 跑完导师的测试不代表你已经理解后续阶段。每课只需给出运行结果、一个预测和一段解释；阶段末确认后再继续。

## 1. 获取正确分支

GitHub 上选择 `arena/01a0981c-exercise-project-as-ai-enginne`。本会话所有课程修改都在这个分支，不自动合并到 main。已有本地修改时先备份或提交，避免盲目覆盖。

可直接在当前 Arena 工作区学习，也可下载此分支在自己的电脑操作。课程命令默认终端位于仓库根目录。

## 2. 解释器和虚拟环境

推荐 Python 3.11，1A 只用标准库，可以直接运行。1B 开始使用包结构与测试：

```bash
python --version
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell 改用：.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m examples.load_manuals
python -m pytest tests/test_search.py -q
```

某些系统命令为 `python3` 或 Windows 的 `py -3.11`，创建环境后再使用该环境的 Python。不要用不同解释器的 pip 安装，然后用系统 Python 运行。

当前已经提供 `pyproject.toml`、`src/` 和测试，不需要再手工新建。`python -m examples.xxx` 必须从仓库根目录运行；包中的 CLI 以 `python -m evidencedesk.search` 运行。

## 3. 按课安装

| 小课 | 增加的依赖 | 网络/费用条件 |
|---|---|---|
| 1A | 无 | 完全离线 |
| 1B–2A、4A 的公式、5C 缓存、6B、7B、8B | `.[dev]` | 首次安装 pytest 需网络，运行不需模型 |
| 2B | `.[ingest]` | PyPDF 本地；tiktoken 首次可能下载编码表 |
| 3A | `.[vector]` | Qdrant 本地内存模式，无远端服务 |
| 3B | `.[llm,vector]` | 在线 embedding/chat，会外发文本并产生费用 |
| 4B 真实对照 | `sentence-transformers` 与 `.[llm]` | 模型下载、RAM/磁盘需求、可选 GPU；查询改写会付费 |
| 5A/5B | `.[web,dev]` 与 Node.js 22 | `npm --prefix frontend ci` 后编译；API 不调用 LLM |
| 5C PostgreSQL | 本机已有 PostgreSQL/psql | 专用实验数据库，未包含自动创建数据库的脚本 |
| 6A | `.[workflow]` | LangGraph 在本机执行，不使用 LLM |
| 7A Ragas | 单独环境 `ragas>=0.3,<0.4` 与 llm extra | 参考接口属于 0.3 系列，需兼容性检查和裁判模型费用 |
| 7A LangSmith | langsmith（已由 LangChain 依赖引入） | 需要服务账号、项目和明确的数据上传授权 |
| 8A | Docker（可选本机安装） | 镜像下载；部署到云需你确认供应商和预算 |
| 9A | 独立环境 `.[advanced,llm]` | 未测试 Deep Agents 安装组合，核对版本后再运行 |
| 9B | `mcp>=1,<2` | 本地协议往返，不用模型 |

`requirements-tested.lock.txt` 是本轮实际测试环境的 `pip freeze` 快照（移除了本地 editable 路径），不是覆盖所有平台、带哈希的全栈锁；里面也不包含未运行的所有大型模型依赖。只想开始学习时不要安装它；需要重现整套已测试示例/CI 时才使用。

```bash
python -m pip install -r requirements-tested.lock.txt
python -m pip install --no-deps -e .
```

首次安装仍需网络。源代码中的 optional extras 给出允许的主版本范围，实际升级后需重新运行测试，不能盲目将不同课程依赖合并到一个环境。

## 4. 密钥与在线实验

预算为零时，先看 [免费路线](zero-budget.md)，不要求购买 OpenAI API。本轮新增 Agnes dry-run 和真实本地 PostgreSQL 验证；后者另装 `requirements-database.txt`，不强制塞入基础课程依赖。

- 不在 Git、截图、聊天或命令历史里写入实际密钥。
- `.env` 已忽略，但脚本**不自动读取 `.env`**。使用 IDE 的安全环境配置、系统凭据工具，或终端隐藏输入后设置进程环境。
- Bash 可用 `read -rs OPENAI_API_KEY; export OPENAI_API_KEY` 临时输入；不要把密钥打印出来。结束后 `unset OPENAI_API_KEY`。
- CHAT_MODEL、EMBEDDING_MODEL、JUDGE_MODEL 由你账户的可用模型决定；不预填未经账户验证的名称。
- 上线前在供应商侧限制预算、检查配额，并明确资料是否允许外发。单次 max_tokens、超时和步数不构成账户硬费用上限。
- 所有样例手册均为虚构资料；不要直接替换成真实企业文件来测试。

## 5. 前端与预览

```bash
npm --prefix frontend ci --ignore-scripts
npm --prefix frontend run build
# Bash，Windows 用 $env:EVIDENCEDESK_DEMO="1"
export EVIDENCEDESK_DEMO=1
uvicorn evidencedesk.api:app --host 0.0.0.0 --port 8000
```

前端和 API 同源，浏览器使用 `/api/search`。远程预览点工作区提供的预览地址，不在浏览器代码里写 localhost。当前页面只展示词法候选证据，演示 token 是公开固定值，不可用于真实数据。

只有需要交互学习 5A/5B 时才启动长驻服务；备齐教材不要求一直开服务。运行后按 Ctrl+C 结束本机服务。

## 6. 修改和提问

正确作答后，导师会把题目、你的回答、标准答案与解析写入对应课程的“已完成问答与标准答案”，便于日后复习；尚未答的题不提前归档。

每课明确给出改哪一处、为什么改、如何运行、预期是什么。临时改变后恢复参考版本，或保存为单独学习笔记。不要为了全绿修改原始金标准。

你可以直接说“请逐行讲 4B 第二段”，不必整章读完才提问。调试信息：文件/行号、运行命令、完整错误栈、预期与实际；隐去密钥和个人信息即可。
