# 项目路线：让每项技术都有问题可解决

## 目标架构（不是当前实现）

```text
TypeScript 前端 → FastAPI → 身份与检索权限 → 检索 → 证据检查 → 回答与引用
                          │                   ↑
                          │         文档 → 清洗/分块 → 向量与词法索引
                          └→ 受控工作流 → 人工审批 → 工单工具
PostgreSQL：文档版本/权限/审批记录；Qdrant：向量与元数据过滤
离线评测 + pytest + 运行追踪 + Docker + GitHub Actions
```

主线采用 Python、FastAPI、Qdrant、LangChain/LangGraph、PostgreSQL、TypeScript。阶段 1 完全离线，不花模型费用；后续 embedding/LLM 可按设备、隐私和预算选本地或托管方案。在引入付费服务前确认预算。

下表是**规划，不是已完成的成果**。每个阶段都要走“问题 → 原理 → 实现 → 验证 → 反思”；只有当前阶段展开详细课程，验收后询问是否继续。

| 阶段 | 问题与即时引入的原理/技术 | 你实现什么 | 如何验证理解与结果 | 产出及反思 | 卡住时参考 |
|---|---|---|---|---|---|
| 1. 证据优先的离线基线 | 不接模型，能否稳定找到回答依据？Python 模块、文档 ID、词法检索、Recall@k、pytest | 加载虚构手册、词语覆盖基线、CLI、评测与测试 | 8 条开发题、边界测试、解释关键词漏召回原因；不要求语义题全对 | 可运行基线、失败分析；区分检索结果与答案 | 本仓库第一课；Python/pytest 官方文档 |
| 2. 可追溯的数据管道 | 文档长、格式杂、会更新，如何避免脏数据与重复索引？PyPDF、清洗、分块、token、哈希与版本 | PDF/Markdown 加载、稳定 chunk ID、来源页码、增量更新；必要时才用 Unstructured | 重跑无重复、更新可删除旧块、空文档报错；解释字符与 token 差异 | 入库管道、分块实验；反思表格/扫描件局限 | python-ai-learn；PyPDF、tiktoken 官方文档 |
| 3. 最小可信 RAG | 词不同但语义相同怎么办？embedding、相似度、Qdrant、上下文生成、结构化引用 | 选一种嵌入方案；先显式实现检索→提示→生成，再用 LangChain 封装；建立无证据拒答 | 同题对比词法/向量；检查引用能否支持结论、索引/查询模型一致；测延迟费用 | 带引用的 CLI RAG、首个对照实验；分析幻觉 | LangChain/Qdrant 官方文档；Agent_Rag_Study |
| 4. 有依据的检索优化 | 错误来自召回、排序还是上下文丢失？BM25+向量融合、rerank、多查询、父子检索 | 根据失败类型一次只加一种策略；实现评测脚本；使用 Pandas 分析结果 | 固定语料/问题/参数，报告 Recall@k、MRR、延迟；设计隔离最终测试集 | 消融报告；有效且成本可接受才保留策略 | rag-mastery-path；Ragas 官方文档 |
| 5. 面向用户的安全产品 | CLI 无法多人使用，流式响应如何可靠交付？FastAPI、SSE、TS、PostgreSQL、身份与 ACL | API、前端、引用跳转、会话存储；请求身份由服务端验证，向量检索前过滤权限 | API/契约测试；跨用户/租户隔离；取消请求与断流；恶意文档测试 | 可演示 Web 应用、威胁模型；评估失败体验 | python-ai-learn；FastAPI、PostgreSQL 官方文档 |
| 6. 从问答到受控行动 | 如何由证据协助建工单而不误操作？Function Calling、LangGraph、持久化状态、人工审批、幂等 | 先实现固定流程；生成工单草稿→确认→工具执行；工具重校验身份与审批 | 未审批不能写、重试不重复创建、越权/参数注入失败；解释为何不需要无限自主循环 | 可恢复的工单工作流；对照 Chain 与 Agent 的必要性 | Build-a-RAG-agent-with-LangChain；agentic-ai；LangGraph 官方文档 |
| 7. 评估、记忆与运行诊断 | 多轮使用后，如何知道变差了或记错了？回归集、Ragas、LangSmith、短期状态与长期记忆 | 人工标注结合自动评测；脱敏追踪；会话裁剪；经同意的偏好记忆、删除/过期机制 | 回归门槛；记忆跨用户不串用，撤回后不可召回；LLM 裁判与人工校准 | 评测看板、成本/延迟记录、记忆策略；分析评分偏差 | Ragas/LangSmith 官方文档；ai-agents-from-zero |
| 8. 部署与作品集 | 别人能否一键运行并复现你的结论？Docker、CI、配置、健康检查、云部署 | 容器、GitHub Actions、端到端 smoke test、无密钥离线测试；部署前确认费用 | 干净环境启动、失败回滚演练、无密钥泄露、权限用例通过 | 演示视频、架构图、实测结果、限制与简历描述 | python-ai-learn；AI-Engineer-Journey；Ai-Engineering-Roadmap |
| 9. 可选的复杂任务实验 | 单流程无法完成多资料研究时才需要什么？Deep Agents、子任务隔离、MCP | 在阶段 6 对照组之上实现受限研究/报告任务、只读 MCP 接口；需要时才开子 Agent | 对比成功率、token、延迟、错误传播；限制工具权限、步数与预算 | 技术决策记录：采用或不采用，都要有证据 | deepagents-learn；deepagents-in-action；Deep Agents 官方文档 |

## 技术覆盖不是安装清单

| 技术族 | 默认选择与引入条件 | 替代/扩展，不强塞入主线 |
|---|---|---|
| LLM 框架 | LangChain：阶段 3 重复调用代码出现后；LangGraph：阶段 6 可恢复审批 | LlamaIndex 用于检索管道对照，不再维护第二套完整应用；Deep Agents 只在阶段 9 有复杂任务证据时用 |
| 向量索引 | Qdrant：向量检索和元数据过滤 | Chroma/FAISS 可作为本地原型对照；Pinecone 只在明确需要托管且预算允许时评估，不四套全接 |
| 嵌入 | 阶段 3 对照小样本后选定一套模型和版本 | HuggingFace 是模型/工具生态，BGE 是模型系列，sentence-transformers 是加载/推理库；OpenAI 是托管方案，四者不是同一层级 |
| 提示 | PromptTemplate、结构化 schema、引用约束；格式不稳时才加 Few-shot | ReAct 用于工具交互；CoT 只讲分解问题与可验证的外部步骤，不索取或记录模型内部思维链 |
| 记忆 | 短期会话状态/摘要与用户授权的长期偏好 | ConversationBufferMemory 作为历史概念比较，使用时查当前兼容 API；向量记忆不是事实真相，必须隔离、过期、可删除 |
| 评估 | pytest 验证确定行为，Ragas 辅助答案评估，LangSmith 诊断调用链 | TruLens 在需要不同反馈方案时做小规模对比，不建立重复监控体系 |
| 服务与存储 | FastAPI + TS 前端 + PostgreSQL；确认负载瓶颈后才引入 Redis | Streamlit/Gradio 可用于临时原型，不并行维护三套 UI；LangServe 仅在服务接口需求匹配时考虑 |
| 安全 | 从第一天不放真实信息/密钥；多人产品前落实 ACL | 扫描文档作为不可信数据；检索、缓存、日志、记忆、工具都不能绕过授权 |

## 最终验收标准（到相应阶段再落成测试）

- 固定数据版本和实验配置；保留词法基线与优化后的真实对照，不承诺预设提升数字。
- 正常题、无答案题、冲突/过期题、权限题、提示注入题均有测试；最终保留集不用于调参。
- 引用可定位到文档版本/页码或段落；有引用不等于正确，还需验证其支持结论。
- 外部写操作需要审批、授权、参数校验、审计与幂等；模型不是权限系统。
- 可在无付费密钥条件下运行确定性测试；在线集成测试单独启用。
- README 如实说明数据是虚构的、模型依赖、成本、限制以及未解决的问题。

## 参考导航

以下为任务提供的学习资源入口，**此处未逐项核验内容或版本**；进入具体技术阶段前再核对官方文档和教程依赖，不直接照搬旧 API。

- Python 工程化：https://github.com/Pjk-llm/python-ai-learn
- Deep Agents 课程：https://github.com/Pjk-llm/deepagents-learn
- RAG 进阶：https://github.com/SIGILIPELLI/rag-mastery-path
- RAG 架构对比：https://github.com/Fortune-Ndlovu/Build-a-RAG-agent-with-LangChain
- LangChain 练习：https://github.com/RudyGo8/Agent_Rag_Study
- Deep Agents 进阶：https://github.com/datawhalechina/deepagents-in-action
- Agent 概念：https://github.com/datawhalechina/agentic-ai
- 端到端参考：https://github.com/didilili/ai-agents-from-zero
- Deep Agents 官方：https://docs.langchain.com/oss/python/deepagents/overview
- 技术路线：https://github.com/Semicolon101/Ai-Engineering-Roadmap
- 项目节奏：https://github.com/dan2mcdr/AI-Engineer-Journey
