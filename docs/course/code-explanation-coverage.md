# 项目代码讲解覆盖清单

[课程目录](index.md) · [当前 2A](../lessons/02a-chunks-versions.md)

核查日期：2026-09-18。基准：`8a7c4be` 的受 Git 管理文件；本轮只增加文档，不改变下列实现文件。

## 结论：没有完成全仓库逐行精讲

22 节课程已准备，不等于项目内每份文件、每行代码都已精讲。主线教材有完整源码、就近注释及“逐行/相邻语句”说明，但很多说明以若干行组成的语句组呈现，不能一概称为达到 1A 的逐行讲解细度。

三个维度必须分开：教材已写好、讲解是否逐句充分、学习者是否已经学过并验收。当前教学仅到 2A；未来课程有文档不等于对话里已经讲过，阶段基础验收也不是逐文件逐行掌握证明。

## 核查口径与数量

- 本表列 51 个受 Git 管理的实现/示例/测试/工具/前端文件，以及 Dockerfile、主线 pyproject 和 CI 配置。包含两个仅有模块说明字符串的包入口。
- 35 个文件在课程中有 `<!-- source: ... -->` 标记的完整源码副本；这些副本已核对与当前源文件一致，**不是 35 份均已完成人工逐行精讲的证明**。
- `examples/01_read_document.py` 没有该标记，但 1A 确实有完整示例和按具体行解释；不能因缺少标记就算成没有讲解。
- 两个 `__init__.py` 仅含模块说明，没有业务执行逻辑，单独列示。
- 另有 13 个有实质内容的文件，尚未纳入上述完整文件级讲解；其中部分已有用途、运行步骤或行内注释，不等于完全没有文档，也不等于逐行精讲已完成。
- 其他 JSON/TOML 配置、锁文件、依赖列表与忽略规则另列，不将它们假装纳入“51 个代码文件都覆盖”的统计。原始数据、第三方依赖、构建产物和学员本机未提交的 scratch/test 文件不在本次清单内。

`tools/check_course.py` 检查源码副本一致性、本地链接、课数及部分目录的 Python 语法；它不会判断每行是否解释充分，更不能判断学习者是否掌握。因此其 PASS 不能用作全仓库讲解覆盖率。

## 逐文件入口

表中“主线源码＋语句组讲解”表示已有材料入口，**不是严格逐行精讲已验收**。行数为空行、注释在内的物理行数，仅帮助估计阅读范围。

| 文件 | 行数 | 当前讲解状态 | 教材入口 |
|---|---:|---|---|
| [.github/workflows/course.yml](../../.github/workflows/course.yml) | 25 | 主线源码＋语句组讲解；细度未逐行审定 | [08a-deploy-ci](../lessons/08a-deploy-ci.md) |
| [deploy/Dockerfile](../../deploy/Dockerfile) | 22 | 主线源码＋语句组讲解；细度未逐行审定 | [08a-deploy-ci](../lessons/08a-deploy-ci.md) |
| [deploy/schema.sql](../../deploy/schema.sql) | 24 | 主线源码＋语句组讲解；细度未逐行审定 | [05c-postgres-cache](../lessons/05c-postgres-cache.md) |
| [examples/01_read_document.py](../../examples/01_read_document.py) | 17 | 有按具体行的手工讲解 | [1A](../lessons/01a-read-document.md) |
| [examples/__init__.py](../../examples/__init__.py) | 1 | 仅模块说明；无业务执行语句 | 包入口，不计作缺失的复杂逻辑讲解 |
| [examples/agnes_rag.py](../../examples/agnes_rag.py) | 21 | 待补完整文件级讲解 | 现有用途说明/行内注释不能替代逐行精讲 |
| [examples/approval_graph.py](../../examples/approval_graph.py) | 43 | 主线源码＋语句组讲解；细度未逐行审定 | [06a-langgraph](../lessons/06a-langgraph.md) |
| [examples/approved_ticket.py](../../examples/approved_ticket.py) | 22 | 主线源码＋语句组讲解；细度未逐行审定 | [06b-authorized-tools](../lessons/06b-authorized-tools.md) |
| [examples/cache_scope.py](../../examples/cache_scope.py) | 19 | 主线源码＋语句组讲解；细度未逐行审定 | [05c-postgres-cache](../lessons/05c-postgres-cache.md) |
| [examples/chunk_versions.py](../../examples/chunk_versions.py) | 19 | 主线源码＋语句组讲解；细度未逐行审定 | [02a-chunks-versions](../lessons/02a-chunks-versions.md) |
| [examples/deep_research.py](../../examples/deep_research.py) | 29 | 主线源码＋语句组讲解；细度未逐行审定 | [09a-deepagents](../lessons/09a-deepagents.md) |
| [examples/hybrid_rankings.py](../../examples/hybrid_rankings.py) | 13 | 主线源码＋语句组讲解；细度未逐行审定 | [04a-hybrid](../lessons/04a-hybrid.md) |
| [examples/judge_answer.py](../../examples/judge_answer.py) | 24 | 主线源码＋语句组讲解；细度未逐行审定 | [07a-eval-observability](../lessons/07a-eval-observability.md) |
| [examples/langsmith_metrics.py](../../examples/langsmith_metrics.py) | 18 | 主线源码＋语句组讲解；细度未逐行审定 | [07a-eval-observability](../lessons/07a-eval-observability.md) |
| [examples/live_rag.py](../../examples/live_rag.py) | 52 | 主线源码＋语句组讲解；细度未逐行审定 | [03b-live-rag](../lessons/03b-live-rag.md) |
| [examples/live_variants.py](../../examples/live_variants.py) | 40 | 主线源码＋语句组讲解；细度未逐行审定 | [04b-rerank-multiquery](../lessons/04b-rerank-multiquery.md) |
| [examples/load_manuals.py](../../examples/load_manuals.py) | 11 | 主线源码＋语句组讲解；细度未逐行审定 | [01b-structured-loading](../lessons/01b-structured-loading.md) |
| [examples/make_demo_pdf.py](../../examples/make_demo_pdf.py) | 22 | 主线源码＋语句组讲解；细度未逐行审定 | [02b-pdf-tokens](../lessons/02b-pdf-tokens.md) |
| [examples/mcp_client.py](../../examples/mcp_client.py) | 25 | 主线源码＋语句组讲解；细度未逐行审定 | [09b-mcp](../lessons/09b-mcp.md) |
| [examples/mcp_server.py](../../examples/mcp_server.py) | 20 | 主线源码＋语句组讲解；细度未逐行审定 | [09b-mcp](../lessons/09b-mcp.md) |
| [examples/memory_lifecycle.py](../../examples/memory_lifecycle.py) | 17 | 主线源码＋语句组讲解；细度未逐行审定 | [07b-memory](../lessons/07b-memory.md) |
| [examples/pdf_tokens.py](../../examples/pdf_tokens.py) | 25 | 主线源码＋语句组讲解；细度未逐行审定 | [02b-pdf-tokens](../lessons/02b-pdf-tokens.md) |
| [examples/portfolio_snapshot.py](../../examples/portfolio_snapshot.py) | 25 | 主线源码＋语句组讲解；细度未逐行审定 | [08b-portfolio](../lessons/08b-portfolio.md) |
| [examples/retrieval_variants.py](../../examples/retrieval_variants.py) | 16 | 主线源码＋语句组讲解；细度未逐行审定 | [04b-rerank-multiquery](../lessons/04b-rerank-multiquery.md) |
| [examples/trace_allowlist.py](../../examples/trace_allowlist.py) | 19 | 主线源码＋语句组讲解；细度未逐行审定 | [07a-eval-observability](../lessons/07a-eval-observability.md) |
| [examples/vector_geometry.py](../../examples/vector_geometry.py) | 21 | 主线源码＋语句组讲解；细度未逐行审定 | [03a-vector-geometry](../lessons/03a-vector-geometry.md) |
| [frontend/client.ts](../../frontend/client.ts) | 42 | 主线源码＋语句组讲解；细度未逐行审定 | [05b-typescript-ui](../lessons/05b-typescript-ui.md) |
| [frontend/index.html](../../frontend/index.html) | 11 | 待补完整文件级讲解 | 现有用途说明/行内注释不能替代逐行精讲 |
| [pyproject.toml](../../pyproject.toml) | 30 | 主线源码＋语句组讲解；细度未逐行审定 | [01d-cli-tests](../lessons/01d-cli-tests.md) |
| [src/evidencedesk/__init__.py](../../src/evidencedesk/__init__.py) | 1 | 仅模块说明；无业务执行语句 | 包入口，不计作缺失的复杂逻辑讲解 |
| [src/evidencedesk/agnes.py](../../src/evidencedesk/agnes.py) | 78 | 待补完整文件级讲解 | 现有用途说明/行内注释不能替代逐行精讲 |
| [src/evidencedesk/api.py](../../src/evidencedesk/api.py) | 56 | 主线源码＋语句组讲解；细度未逐行审定 | [05a-api-security](../lessons/05a-api-security.md) |
| [src/evidencedesk/documents.py](../../src/evidencedesk/documents.py) | 35 | 主线源码＋语句组讲解；细度未逐行审定 | [01b-structured-loading](../lessons/01b-structured-loading.md) |
| [src/evidencedesk/evaluate.py](../../src/evidencedesk/evaluate.py) | 50 | 主线源码＋语句组讲解；细度未逐行审定 | [01e-evaluation](../lessons/01e-evaluation.md) |
| [src/evidencedesk/hybrid.py](../../src/evidencedesk/hybrid.py) | 43 | 主线源码＋语句组讲解；细度未逐行审定 | [04a-hybrid](../lessons/04a-hybrid.md) |
| [src/evidencedesk/ingest.py](../../src/evidencedesk/ingest.py) | 27 | 主线源码＋语句组讲解；细度未逐行审定 | [02a-chunks-versions](../lessons/02a-chunks-versions.md) |
| [src/evidencedesk/memory.py](../../src/evidencedesk/memory.py) | 30 | 主线源码＋语句组讲解；细度未逐行审定 | [07b-memory](../lessons/07b-memory.md) |
| [src/evidencedesk/search.py](../../src/evidencedesk/search.py) | 55 | 主线源码＋语句组讲解；细度未逐行审定 | [01c-lexical-search](../lessons/01c-lexical-search.md) |
| [src/evidencedesk/tickets.py](../../src/evidencedesk/tickets.py) | 37 | 主线源码＋语句组讲解；细度未逐行审定 | [06b-authorized-tools](../lessons/06b-authorized-tools.md) |
| [tests/test_agnes.py](../../tests/test_agnes.py) | 70 | 待补完整文件级讲解 | 现有用途说明/行内注释不能替代逐行精讲 |
| [tests/test_api.py](../../tests/test_api.py) | 83 | 主线源码＋语句组讲解；细度未逐行审定 | [05a-api-security](../lessons/05a-api-security.md) |
| [tests/test_core.py](../../tests/test_core.py) | 97 | 待补完整文件级讲解 | 现有用途说明/行内注释不能替代逐行精讲 |
| [tests/test_integrations.py](../../tests/test_integrations.py) | 49 | 待补完整文件级讲解 | 现有用途说明/行内注释不能替代逐行精讲 |
| [tests/test_search.py](../../tests/test_search.py) | 57 | 主线源码＋语句组讲解；细度未逐行审定 | [01d-cli-tests](../lessons/01d-cli-tests.md) |
| [tests/test_space_export.py](../../tests/test_space_export.py) | 12 | 待补完整文件级讲解 | 现有用途说明/行内注释不能替代逐行精讲 |
| [tools/check_course.py](../../tools/check_course.py) | 29 | 待补完整文件级讲解 | 现有用途说明/行内注释不能替代逐行精讲 |
| [tools/export_space.py](../../tools/export_space.py) | 33 | 待补完整文件级讲解 | 现有用途说明/行内注释不能替代逐行精讲 |
| [tools/fetch_public_manuals.py](../../tools/fetch_public_manuals.py) | 53 | 待补完整文件级讲解 | 现有用途说明/行内注释不能替代逐行精讲 |
| [tools/local_postgres.py](../../tools/local_postgres.py) | 57 | 待补完整文件级讲解 | 现有用途说明/行内注释不能替代逐行精讲 |
| [tools/postgres_lab.py](../../tools/postgres_lab.py) | 100 | 待补完整文件级讲解 | 现有用途说明/行内注释不能替代逐行精讲 |
| [tools/sync_course_sources.py](../../tools/sync_course_sources.py) | 41 | 待补完整文件级讲解 | 现有用途说明/行内注释不能替代逐行精讲 |

## 其他配置与维护文件

下列文件在项目内，但不属于上表源文件口径；本轮没有逐项认定已经完整讲解。锁文件应重点解释用途、生成方式和更新风险，不把解释每个第三方依赖条目当成学习前提。

- [.dockerignore](../../.dockerignore)
- [.gitignore](../../.gitignore)
- [data/sources/fastapi.json](../../data/sources/fastapi.json)
- [frontend/package-lock.json](../../frontend/package-lock.json)
- [frontend/package.json](../../frontend/package.json)
- [frontend/tsconfig.json](../../frontend/tsconfig.json)
- [requirements-database.txt](../../requirements-database.txt)
- [requirements-tested.lock.txt](../../requirements-tested.lock.txt)
- [tools/postgres-runtime/package-lock.json](../../tools/postgres-runtime/package-lock.json)
- [tools/postgres-runtime/package.json](../../tools/postgres-runtime/package.json)

## 怎样补齐，而不跳过当前学习阶段

这是一份缺口清单，不是本轮已完成补写的声明。若按“全项目逐行精讲”要求补齐，建议分为：

1. 主线代码：将宽泛的多行概括展开到具体语句，解释语法、输入输出、数据变化、边界和设计理由。
2. 配套测试：说明各 fixture/断言保护什么行为，以及什么错误会让它失败，而不是只介绍如何运行 pytest。
3. 零预算与工程工具：补齐 Agnes、公开数据下载、PostgreSQL 实验、Space 导出及课程维护脚本的逐句阅读指南，明确安全/费用/环境边界。
4. HTML 与配置：解释浏览器入口、脚本加载、编译与部署配置；锁文件和第三方内容按用途与维护方式说明。

补写后的文件应明确标记具体覆盖范围，再复核源码一致性；不能仅因有一篇课程、一个注释或复制了源码就标为已精讲。提前补写材料不会自动推进学习者进度，当前仍是 2A。
