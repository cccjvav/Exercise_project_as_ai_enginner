# 逐行教材补全：验证记录

日期：2026-09-19。[源码目录](index.md) · [覆盖范围](../course/code-explanation-coverage.md)

## 本轮实际运行

| 检查 | 实际结果与边界 |
|---|---|
| `python -m pytest -q -rs` | **63 passed，0 skipped，1 warning**；包括实际本地Qdrant、LangGraph、MCP、PDF样例与空页拒绝，以及API、Agnes mock、Space白名单测试。不是实际模型推理。 |
| `npm --prefix frontend ci --ignore-scripts` / `npm --prefix frontend run build` | 安装与TypeScript编译成功；没有启动浏览器E2E，也未构建Docker镜像。 |
| 原八题，`evaluate --k 1` | Recall/MRR各5/6，无答案空返回率1；q06仍空候选。 |
| 固定九题，`--questions data/regression/phase1-v1.jsonl --k 3` | Recall/MRR各5/6，无答案空返回率2/3；q06空候选，q09返回webhook-delivery、score=1、recall=null。两题仍未解决。 |

测试警告来自Starlette TestClient对anyio旧BlockingPortal别名的弃用提醒；不是测试失败，但未来升级仍需跟踪。

### 本轮环境（不是冒称重装了旧锁）

Python 3.11.2 / Linux x86_64；Node 22.22.3 / npm 10.9.8。新虚拟环境安装本项目`dev,web,vector,ingest,workflow` extras及MCP，版本包括：pytest8.4.2、FastAPI0.141.1、httpx0.28.1、qdrant-client1.19.1、LangGraph1.2.11、MCP1.30.0、pypdf6.19.0、tiktoken0.14.0。

本轮没有更新`requirements-tested.lock.txt`。本环境部分版本与历史快照不同；“63项通过”是这个环境的实际结果，不是证明旧快照在所有平台可复现。

## 教材机械核对

已实际完成以下核对：

- `python tools/check_course.py`：**22课、96份完整源码副本一致**（原35份＋新51份主文件＋10份补充配置），本地链接、清单源码SHA256/行数/逐行锚点及指定目录Python语法通过。
- 独立核查51页的**1779个行号与逐行源码片段**，顺序、内容和说明存在性全部匹配；另对包含tools在内的全部已跟踪Python文件执行AST语法解析。
- 将22课新增导航块移除后，与补写前Git版本逐字比较：**原课程正文及学习档案均未改变**。
- 在隔离临时副本分别注入“完整源码漂移、缺一行锚点、坏本地链接、过期hash”四种错误：检查器都实际拒绝；恢复后重新通过。没有用真实课程/用户文件做破坏性测试。
- `git diff --check`通过。应用业务源码、语料、题集和学员未跟踪笔记未改；唯一实现变更为课程维护检查器扩展。

这些检查验证对应关系和回归保护，**不会自动评分每行解释是否充分，更不能替学习者通过课程**。解释内容按源码人工编写复核；若某行仍不易懂，应在该页继续增加具体演算，而不是拿通过数量挡住问题。

本页记录本地实际结果；提交/推送和GitHub远端CI状态是另一层证据，不从本地PASS推断云端部署成功。

## 本轮没有做

- 没有真实Agnes/OpenAI/Ragas/Deep Agent调用，没有模型下载或LangSmith上传。
- 没有重新下载公开语料、启动/重启PostgreSQL、重跑RLS；早先数据库实验属于历史记录，不冒充本轮。
- 没有创建云库、上传Space、构建Docker或确认用户浏览器401已经消失。
- PDF集成测试验证文字层和空页拒绝，**不证明tiktoken编码表网络下载成功**。
- 没有把提前准备的未来课程、测试通过或新增练习归档为学员已完成。

## 当前教学状态

阶段1基础验收保留；阶段2已获同意，当前2A/Q1–Q4已归档但2A未验收。来源脚本、版本/更新等后续学习按原课继续；q06/q09跨阶段跟踪不变。
