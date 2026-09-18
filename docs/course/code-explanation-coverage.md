# 项目代码讲解覆盖清单

[课程目录](index.md) · [源码逐行总目录](../code/index.md) · [当前2A](../lessons/02a-chunks-versions.md)

核查日期：2026-09-19。上一轮审计发现“22课齐备”不等于“所有源文件1A细度”；本轮按用户授权对**全部主清单**补写/展开，而非只补原13个实质缺口。

## 本轮交付范围

- **51份主清单文件，1779个物理行**：完整源码、每行定位与解释、输入输出、风险、数据演算、一个关键练习及复盘。原35份已有源码/分组说明也补成逐行页；1A原讲解保留；两个仅说明字符串的包入口单列解释。
- **10份补充配置/维护文件**：忽略规则和小配置逐项讲，依赖锁讲结构/固定版本/更新流程，不冒称逐条解释第三方库实现。
- 新增材料在docs/code；22课只增加阅读入口，保留原来的任务与1A–2A作答档案。**学习仍是2A/Q1–Q4已归档、未验收**。
- 第三方安装目录、生成物、原始/处理数据正文、机器本地未提交scratch/test与用户笔记不计入源码范围。新业务文件加入时应更新此清单，不能拿51作为永久分母。

物理行数包含空行/注释；较上轮1766增加13行，来自`tools/check_course.py`增加hash/行号清单校验。应用、例子、测试、前端、SQL和部署业务行为本轮未更改。

## 质量与验证不是同一件事

每份逐行页都解释具体语句的语法、数据流、理由与边界。检查器可核对源码副本、hash、行数与逐行锚点，**不能自动评判讲解充分、内容事实正确或学习者掌握**；这些仍需人工校读和分阶段练习。具体实测与未运行项见[验证记录](../code/validation.md)。

## 逐文件入口

| 文件 | 行数 | 本轮材料 |
|---|---:|---|
| [.github/workflows/course.yml](../../.github/workflows/course.yml) | 25 | [完整源码＋逐行精讲＋关键练习](../code/_github--workflows--course_yml.md) |
| [deploy/Dockerfile](../../deploy/Dockerfile) | 22 | [完整源码＋逐行精讲＋关键练习](../code/deploy--Dockerfile.md) |
| [deploy/schema.sql](../../deploy/schema.sql) | 24 | [完整源码＋逐行精讲＋关键练习](../code/deploy--schema_sql.md) |
| [examples/01_read_document.py](../../examples/01_read_document.py) | 17 | [完整源码＋逐行精讲＋关键练习](../code/examples--01_read_document_py.md) |
| [examples/__init__.py](../../examples/__init__.py) | 1 | [完整源码＋逐行精讲＋关键练习](../code/examples--__init___py.md) |
| [examples/agnes_rag.py](../../examples/agnes_rag.py) | 21 | [完整源码＋逐行精讲＋关键练习](../code/examples--agnes_rag_py.md) |
| [examples/approval_graph.py](../../examples/approval_graph.py) | 43 | [完整源码＋逐行精讲＋关键练习](../code/examples--approval_graph_py.md) |
| [examples/approved_ticket.py](../../examples/approved_ticket.py) | 22 | [完整源码＋逐行精讲＋关键练习](../code/examples--approved_ticket_py.md) |
| [examples/cache_scope.py](../../examples/cache_scope.py) | 19 | [完整源码＋逐行精讲＋关键练习](../code/examples--cache_scope_py.md) |
| [examples/chunk_versions.py](../../examples/chunk_versions.py) | 19 | [完整源码＋逐行精讲＋关键练习](../code/examples--chunk_versions_py.md) |
| [examples/deep_research.py](../../examples/deep_research.py) | 29 | [完整源码＋逐行精讲＋关键练习](../code/examples--deep_research_py.md) |
| [examples/hybrid_rankings.py](../../examples/hybrid_rankings.py) | 13 | [完整源码＋逐行精讲＋关键练习](../code/examples--hybrid_rankings_py.md) |
| [examples/judge_answer.py](../../examples/judge_answer.py) | 24 | [完整源码＋逐行精讲＋关键练习](../code/examples--judge_answer_py.md) |
| [examples/langsmith_metrics.py](../../examples/langsmith_metrics.py) | 18 | [完整源码＋逐行精讲＋关键练习](../code/examples--langsmith_metrics_py.md) |
| [examples/live_rag.py](../../examples/live_rag.py) | 52 | [完整源码＋逐行精讲＋关键练习](../code/examples--live_rag_py.md) |
| [examples/live_variants.py](../../examples/live_variants.py) | 40 | [完整源码＋逐行精讲＋关键练习](../code/examples--live_variants_py.md) |
| [examples/load_manuals.py](../../examples/load_manuals.py) | 11 | [完整源码＋逐行精讲＋关键练习](../code/examples--load_manuals_py.md) |
| [examples/make_demo_pdf.py](../../examples/make_demo_pdf.py) | 22 | [完整源码＋逐行精讲＋关键练习](../code/examples--make_demo_pdf_py.md) |
| [examples/mcp_client.py](../../examples/mcp_client.py) | 25 | [完整源码＋逐行精讲＋关键练习](../code/examples--mcp_client_py.md) |
| [examples/mcp_server.py](../../examples/mcp_server.py) | 20 | [完整源码＋逐行精讲＋关键练习](../code/examples--mcp_server_py.md) |
| [examples/memory_lifecycle.py](../../examples/memory_lifecycle.py) | 17 | [完整源码＋逐行精讲＋关键练习](../code/examples--memory_lifecycle_py.md) |
| [examples/pdf_tokens.py](../../examples/pdf_tokens.py) | 25 | [完整源码＋逐行精讲＋关键练习](../code/examples--pdf_tokens_py.md) |
| [examples/portfolio_snapshot.py](../../examples/portfolio_snapshot.py) | 25 | [完整源码＋逐行精讲＋关键练习](../code/examples--portfolio_snapshot_py.md) |
| [examples/retrieval_variants.py](../../examples/retrieval_variants.py) | 16 | [完整源码＋逐行精讲＋关键练习](../code/examples--retrieval_variants_py.md) |
| [examples/trace_allowlist.py](../../examples/trace_allowlist.py) | 19 | [完整源码＋逐行精讲＋关键练习](../code/examples--trace_allowlist_py.md) |
| [examples/vector_geometry.py](../../examples/vector_geometry.py) | 21 | [完整源码＋逐行精讲＋关键练习](../code/examples--vector_geometry_py.md) |
| [frontend/client.ts](../../frontend/client.ts) | 42 | [完整源码＋逐行精讲＋关键练习](../code/frontend--client_ts.md) |
| [frontend/index.html](../../frontend/index.html) | 11 | [完整源码＋逐行精讲＋关键练习](../code/frontend--index_html.md) |
| [pyproject.toml](../../pyproject.toml) | 30 | [完整源码＋逐行精讲＋关键练习](../code/pyproject_toml.md) |
| [src/evidencedesk/__init__.py](../../src/evidencedesk/__init__.py) | 1 | [完整源码＋逐行精讲＋关键练习](../code/src--evidencedesk--__init___py.md) |
| [src/evidencedesk/agnes.py](../../src/evidencedesk/agnes.py) | 78 | [完整源码＋逐行精讲＋关键练习](../code/src--evidencedesk--agnes_py.md) |
| [src/evidencedesk/api.py](../../src/evidencedesk/api.py) | 56 | [完整源码＋逐行精讲＋关键练习](../code/src--evidencedesk--api_py.md) |
| [src/evidencedesk/documents.py](../../src/evidencedesk/documents.py) | 35 | [完整源码＋逐行精讲＋关键练习](../code/src--evidencedesk--documents_py.md) |
| [src/evidencedesk/evaluate.py](../../src/evidencedesk/evaluate.py) | 50 | [完整源码＋逐行精讲＋关键练习](../code/src--evidencedesk--evaluate_py.md) |
| [src/evidencedesk/hybrid.py](../../src/evidencedesk/hybrid.py) | 43 | [完整源码＋逐行精讲＋关键练习](../code/src--evidencedesk--hybrid_py.md) |
| [src/evidencedesk/ingest.py](../../src/evidencedesk/ingest.py) | 27 | [完整源码＋逐行精讲＋关键练习](../code/src--evidencedesk--ingest_py.md) |
| [src/evidencedesk/memory.py](../../src/evidencedesk/memory.py) | 30 | [完整源码＋逐行精讲＋关键练习](../code/src--evidencedesk--memory_py.md) |
| [src/evidencedesk/search.py](../../src/evidencedesk/search.py) | 55 | [完整源码＋逐行精讲＋关键练习](../code/src--evidencedesk--search_py.md) |
| [src/evidencedesk/tickets.py](../../src/evidencedesk/tickets.py) | 37 | [完整源码＋逐行精讲＋关键练习](../code/src--evidencedesk--tickets_py.md) |
| [tests/test_agnes.py](../../tests/test_agnes.py) | 70 | [完整源码＋逐行精讲＋关键练习](../code/tests--test_agnes_py.md) |
| [tests/test_api.py](../../tests/test_api.py) | 83 | [完整源码＋逐行精讲＋关键练习](../code/tests--test_api_py.md) |
| [tests/test_core.py](../../tests/test_core.py) | 97 | [完整源码＋逐行精讲＋关键练习](../code/tests--test_core_py.md) |
| [tests/test_integrations.py](../../tests/test_integrations.py) | 49 | [完整源码＋逐行精讲＋关键练习](../code/tests--test_integrations_py.md) |
| [tests/test_search.py](../../tests/test_search.py) | 57 | [完整源码＋逐行精讲＋关键练习](../code/tests--test_search_py.md) |
| [tests/test_space_export.py](../../tests/test_space_export.py) | 12 | [完整源码＋逐行精讲＋关键练习](../code/tests--test_space_export_py.md) |
| [tools/check_course.py](../../tools/check_course.py) | 42 | [完整源码＋逐行精讲＋关键练习](../code/tools--check_course_py.md) |
| [tools/export_space.py](../../tools/export_space.py) | 33 | [完整源码＋逐行精讲＋关键练习](../code/tools--export_space_py.md) |
| [tools/fetch_public_manuals.py](../../tools/fetch_public_manuals.py) | 53 | [完整源码＋逐行精讲＋关键练习](../code/tools--fetch_public_manuals_py.md) |
| [tools/local_postgres.py](../../tools/local_postgres.py) | 57 | [完整源码＋逐行精讲＋关键练习](../code/tools--local_postgres_py.md) |
| [tools/postgres_lab.py](../../tools/postgres_lab.py) | 100 | [完整源码＋逐行精讲＋关键练习](../code/tools--postgres_lab_py.md) |
| [tools/sync_course_sources.py](../../tools/sync_course_sources.py) | 41 | [完整源码＋逐行精讲＋关键练习](../code/tools--sync_course_sources_py.md) |

## 补充配置与维护（不混入51份逐行统计）

- [`.dockerignore`](../code/configuration-maintenance.md#config-1)
- [`.gitignore`](../code/configuration-maintenance.md#config-2)
- [`data/sources/fastapi.json`](../code/configuration-maintenance.md#config-3)
- [`frontend/package.json`](../code/configuration-maintenance.md#config-4)
- [`frontend/tsconfig.json`](../code/configuration-maintenance.md#config-5)
- [`requirements-database.txt`](../code/configuration-maintenance.md#config-6)
- [`requirements-tested.lock.txt`](../code/configuration-maintenance.md#config-7)
- [`frontend/package-lock.json`](../code/configuration-maintenance.md#config-8)
- [`tools/postgres-runtime/package.json`](../code/configuration-maintenance.md#config-9)
- [`tools/postgres-runtime/package-lock.json`](../code/configuration-maintenance.md#config-10)

## 进度与回归边界

准备教材≠已运行所有实验≠学员已掌握。q06/q09仍按[固定九题跟踪](regression-cases.md)跨阶段复测；分块、fixture和框架安装都不是修复证据。未来阶段的模型、数据库/云资源与付费动作仍按课程单独确认。
