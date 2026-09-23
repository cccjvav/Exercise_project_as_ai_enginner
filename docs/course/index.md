# EvidenceDesk · 全套课程目录

**版本：2026-09-23 · 9 个阶段，28 节小课。** 22 节原有教材已提前准备；**2026-09-23 修订**新增 2C 语料与保留集，以及 3C/4C/5D/6C/7C 五节集成课（目前为骨架，进入前补齐），见[课程修订记录](course-revision-2026-09-23.md)。**阶段 1（1A–1E）基础验收通过，已确认进入阶段 2，2A 进行中。** 后续内容并未自动验收。

每课遵循：**问题 → 原理 → 完整示例与逐行讲解 → 按步骤做关键改动 → 闭卷小实现 → 验证 → 反思**。示例先给出，不要求对着空文件摸索；重点是看懂数据流、预测一个变化，再实际验证。从 2A 剩余部分起，每课收尾前有一道 10–20 行的闭卷小实现（导师给签名与测试，学习者写函数体），学习用文件由学习者自己提交。

## 先读这些说明

- **[导师接手须知（教学方式 skill）](../../skills/evidencedesk-tutor/SKILL.md)**：接手辅导的助手先读——每条消息一个小示例加一道即兴单题，答后判定、归档、推送；不重新开课，不自动跨阶段。
- [课程修订记录（2026-09-23）](course-revision-2026-09-23.md)：评审结论、学习者三项决定（后端 AI 工程师方向、免费 API 模型路线、全部采纳）、新增课程与最低毕业线。
- [零预算实操方案](zero-budget.md)：免费模型、已运行的真实 PostgreSQL、公开资料、云部署包；顶部有 2026-09-23 的模型路线决定。
- [环境与依赖分层](setup.md)：不要一次装全套模型框架。
- **[1A细度源码逐行精讲](../code/index.md)**：51份主清单完整展开，含测试断言、工程脚本、前端与关键练习；10份补充配置/锁文件单列维护说明。
- [项目代码讲解覆盖清单](code-explanation-coverage.md)：查看具体文件范围、1779行对应关系与质量边界；教材准备不改变当前2A进度。
- [测试与未验证事项](verification.md)：严格区分离线通过、在线待验、生产未完成。
- [组件如何组合成最终作品](integration.md)：教材/组件示例齐备不等于完整产品已经集成。

## 复习已完成的问答

- [1A：路径、文件内容与字段变化](../lessons/01a-read-document.md#已完成问答与标准答案)。
- [1B：加载、数据结构与校验（含纠错和验收小结）](../lessons/01b-structured-loading.md#已完成问答与标准答案)。

- [1C：检索、证据边界、排序与 top-k（含验收小结）](../lessons/01c-lexical-search.md#已完成问答与标准答案)。

- [1D：pytest、CLI 输出约定与类型纠错（含验收小结）](../lessons/01d-cli-tests.md#已完成问答与标准答案)。

- [1E：检索指标、纠错与八题/九题评测](../lessons/01e-evaluation.md#已完成问答与标准答案)。

- [2A：分块、重复量与父文档标识](../lessons/02a-chunks-versions.md#已完成问答与标准答案)。

正确作答后更新对应文档；未完成题不提前归档答案。

## 阶段验收

- [阶段 1：基础验收通过，已确认进入阶段 2](../reviews/phase-01-evidence-baseline.md)。

- [持续回归：q06/q09 的现状、复测节点与固定输入](regression-cases.md)。

## 顺序阅读

| 小课 | 内容 | 当前性质 |
|---|---|---|
| 1A | [读取一份文档](../lessons/01a-read-document.md) | 标准库，逐行讲解 |
| 1B | [从脚本到可靠文档加载器](../lessons/01b-structured-loading.md) | 离线参考实现；已纳入 pytest。 |
| 1C | [词覆盖检索与稳定排序](../lessons/01c-lexical-search.md) | 离线参考实现；已纳入 pytest。 |
| 1D | [CLI、工程配置与测试](../lessons/01d-cli-tests.md) | CLI 和 pytest 已运行；不需要模型密钥。 |
| 1E | [第一次可复现检索评测](../lessons/01e-evaluation.md) | 基线实测见验证报告；非生成式问答评测。 |
| 2A | [分块、来源与幂等更新](../lessons/02a-chunks-versions.md) | 字符分块与内存快照已测试；不是生产持久化索引。 |
| 2B | [PDF、文本层与 token](../lessons/02b-pdf-tokens.md) | PDF 样例提取与空页失败已测；token 编码表下载在本环境遇到 TLS 错误，完整计数未验证。 |
| 2C | [语料扩充、题集标注与冻结保留集](../lessons/02c-corpus-holdout.md) | 规划中骨架（2026-09-23 新增）；语料未生成、题集未标注。 |
| 3A | [向量、余弦相似度与 Qdrant](../lessons/03a-vector-geometry.md) | 真实 Qdrant 本地模式已测；向量为手写几何样例，不是语义模型效果。 |
| 3B | [真实嵌入、LangChain 与有引用回答](../lessons/03b-live-rag.md) | 提供完整在线参考脚本；语法/导入可检查，未发起付费模型调用。到课时补充“提示词是契约”一节与 `base_url` 通用化。 |
| 3C | [集成：/api/answer](../lessons/03c-integrate-answer-api.md) | 规划中骨架（2026-09-23 新增）；主线 API 尚无分块/向量/模型。 |
| 4A | [BM25 与混合检索](../lessons/04a-hybrid.md) | BM25/RRF 机制已测试；演示向量排名为 fixture。 |
| 4B | [重排序、多查询、父子检索与消融](../lessons/04b-rerank-multiquery.md) | 管道连接机制已提供；重排分数与改写排名是明确 fixture，尚未验证真实质量。 |
| 4C | [集成：中文分词、混合检索与真实消融](../lessons/04c-integrate-hybrid-ablation.md) | 规划中骨架（2026-09-23 新增）；分词器与主线接入未实现。 |
| 5A | [FastAPI、授权边界与 SSE](../lessons/05a-api-security.md) | 真实 API/TestClient 已测；公开固定令牌仅用于虚构资料。 |
| 5B | [TypeScript 前端、取消与安全展示](../lessons/05b-typescript-ui.md) | TypeScript 编译已测；尚未做真实浏览器端到端自动化。 |
| 5C | [PostgreSQL、RLS 与缓存隔离](../lessons/05c-postgres-cache.md) | PostgreSQL 18.4 的 documents RLS 已实测；托管云数据库尚未创建。 |
| 5D | [集成：真实身份、PostgreSQL 与 token 流](../lessons/05d-integrate-identity-postgres.md) | 规划中骨架（2026-09-23 新增）；当前身份为公开演示令牌。 |
| 6A | [LangGraph 的暂停、恢复与审批](../lessons/06a-langgraph.md) | 真实 LangGraph 无模型流程已测；checkpoint 只在内存。 |
| 6B | [工具调用、参数校验与幂等](../lessons/06b-authorized-tools.md) | SQLite 模拟工单与重启幂等测试已通过；不连接真实工单系统。 |
| 6C | [集成：工单流经 API](../lessons/06c-integrate-ticket-flow.md) | 规划中骨架（2026-09-23 新增）；审批与工单尚未经过任何 API。 |
| 7A | [回归评测、Ragas 与 LangSmith](../lessons/07a-eval-observability.md) | 离线遥测已运行；Ragas/托管 LangSmith 参考示例未发起在线调用。 |
| 7B | [会话状态与可删除长期记忆](../lessons/07b-memory.md) | 偏好保存、隔离、到期和删除已测；内存实现不持久化。 |
| 7C | [集成：回归门禁与记忆接入](../lessons/07c-integrate-regression-gate.md) | 规划中骨架（2026-09-23 新增）；CI 目前只跑无密钥 pytest。 |
| 8A | [Docker、依赖快照与 CI](../lessons/08a-deploy-ci.md) | 本机测试和 TS 构建已运行；当前环境无 Docker，镜像/云部署与 GitHub 远端检查另行验收。 |
| 8B | [对照报告、演示与求职表达](../lessons/08b-portfolio.md) | 报告生成脚本已运行；不含虚构性能提升或未做的生产部署。 |
| 9A | [Deep Agents 与复杂任务边界](../lessons/09a-deepagents.md) | 完整在线实验脚本；未安装验证 Deep Agents 或调用付费模型。 |
| 9B | [MCP 工具协议与只读集成](../lessons/09b-mcp.md) | 真实 MCP stdio 客户端/服务端往返已测试，无模型调用。 |

## 每个阶段什么时候算通过？

| 阶段 | 关键验收，不是框架数量 |
|---|---|
| 1 | 会解释加载/检索/指标，做过小变式，能区分零匹配与无答案 |
| 2 | 能定位原文，解释字符/token，更新不残留旧块；外部下载失败如实标注；**2C：≥20 份虚构手册、≥40 道分类题、开发/保留集分离并记录哈希** |
| 3 | 实际使用所选免费模型，对引用和拒答做人工核对；未调用模型不能算在线验收；**3C：主线 `/api/answer` 在新语料上跑通，q06/q09 有真实结果** |
| 4 | 固定数据和参数，至少做一个真实对照；fixture 排名不能当质量提升；**4C：中文分词接入，消融在 ≥20 份文档上完成，保留集只跑一次** |
| 5 | API 和浏览器可用、身份可信、权限隔离；演示固定令牌不能用于真实数据；**5D：可信身份替换演示令牌，文档/ACL 入 PostgreSQL，模型输出流式且可取消** |
| 6 | 批准/拒绝/恢复/重试均有证据，真实写操作需受保护审批和授权；**6C：工单流经 API 与数据库，六类审批失败与幂等重试有测试** |
| 7 | 评测与日志不过量外发，记忆隔离可删除，裁判分数经人工校准；**7C：保留集回归门禁进 CI，记忆删除传播有测试** |
| 8 | 干净环境复现、部署实际验证、结果可追溯；简历区分本人改动与参考代码 |
| 9（可选） | 对复杂 Agent/MCP 的必要性、安全和成本做出有证据的采用或舍弃决定 |

完成一个阶段后，导师仍会询问你是否继续。现在不需要按目录连着跑完；想问哪一行就贴出文件和行号。

**最低毕业线（2026-09-23 定）：** 阶段 1–6 完整（含 3C/4C/5D/6C）+ 阶段 8 部署与作品集；阶段 7 至少完成 7C 的回归门禁；阶段 9 可选。达到即可对外展示，不被 28 节绑住。
