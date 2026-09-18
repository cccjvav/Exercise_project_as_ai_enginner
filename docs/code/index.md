# 项目源码逐行精讲 · 1A细度阅读版

[课程目录](../course/index.md) · [覆盖清单](../course/code-explanation-coverage.md) · [当前2A](../lessons/02a-chunks-versions.md) · [本轮验证](validation.md)

**2026-09-19：51份主清单文件、1779个物理行已配套逐行页；另10份配置/锁文件按用途与维护规则讲解。** 原来已有源码的35份也重新展开，不只是补13份缺口。包含空行、注释和两个包入口，但不把这些低复杂度行等同业务语句的教学工作量。

## 怎样使用，而不是一次读完

1. 仍按22课的顺序学习；每课顶部有对应精讲链接。**当前仍为2A，Q1–Q4已归档，2A未验收**，准备未来材料不代表进入未来阶段。
2. 先看“解决什么问题／输入输出／运行与风险”，再看完整源码；按`第N行`定位语法、数据变化、理由和边界。同一物理行有多个表达式时也拆开解释。
3. 每页末尾只选一个关键点练习：给出操作、核对方式和复盘问题，不要求从空文件实现整份代码。在线调用、写库、上传与部署先读风险，等对应课程确认后再做。
4. 测试页逐个解释fixture和assert能发现什么错误；运维脚本标明实际副作用与清理局限；不把mock、手写向量、预置排名当模型质量。
5. 原22课的问题背景、阶段任务和已完成问答全部保留。新页是细读层，不替换历史作答；未答题不填成“学员已完成”。

**本次采用的细度标准：** 每条业务执行语句有针对当前实现的解释；不仅复述行文本，还交代对象/类型或状态如何变、为什么这样写、常见误读与边界。导入/空行/入口保护使用统一语法说明。源码全文、行号齐全只是机械覆盖，解释质量仍须人工核对；遇到不清楚的行可继续按该行加演算。

## 当前2A最直接的入口

- [分块、父ID、正文hash与替换更新](src--evidencedesk--ingest_py.md)：字符与token、parent_id与块ID、返回新字典与持久化事务都分开讲。
- [幂等与正文更新示例](examples--chunk_versions_py.md)。
- [核心测试中的分块断言](tests--test_core_py.md#L36)。
- [q06/q09回归跟踪](../course/regression-cases.md)：两题仍未解决，写完教材不会改动它们的状态。

## 全部文件

| 文件 | 物理行 | 逐行材料 | 对应课程 |
|---|---:|---|---|
| `.github/workflows/course.yml` | 25 | [打开精讲](_github--workflows--course_yml.md) | [08A](../lessons/08a-deploy-ci.md) |
| `deploy/Dockerfile` | 22 | [打开精讲](deploy--Dockerfile.md) | [08A](../lessons/08a-deploy-ci.md) |
| `deploy/schema.sql` | 24 | [打开精讲](deploy--schema_sql.md) | [05C](../lessons/05c-postgres-cache.md) |
| `examples/01_read_document.py` | 17 | [打开精讲](examples--01_read_document_py.md) | [01A](../lessons/01a-read-document.md) |
| `examples/__init__.py` | 1 | [打开精讲](examples--__init___py.md) | 包入口阅读 |
| `examples/agnes_rag.py` | 21 | [打开精讲](examples--agnes_rag_py.md) | [03B](../lessons/03b-live-rag.md) |
| `examples/approval_graph.py` | 43 | [打开精讲](examples--approval_graph_py.md) | [06A](../lessons/06a-langgraph.md) |
| `examples/approved_ticket.py` | 22 | [打开精讲](examples--approved_ticket_py.md) | [06B](../lessons/06b-authorized-tools.md) |
| `examples/cache_scope.py` | 19 | [打开精讲](examples--cache_scope_py.md) | [05C](../lessons/05c-postgres-cache.md) |
| `examples/chunk_versions.py` | 19 | [打开精讲](examples--chunk_versions_py.md) | [02A](../lessons/02a-chunks-versions.md) |
| `examples/deep_research.py` | 29 | [打开精讲](examples--deep_research_py.md) | [09A](../lessons/09a-deepagents.md) |
| `examples/hybrid_rankings.py` | 13 | [打开精讲](examples--hybrid_rankings_py.md) | [04A](../lessons/04a-hybrid.md) |
| `examples/judge_answer.py` | 24 | [打开精讲](examples--judge_answer_py.md) | [07A](../lessons/07a-eval-observability.md) |
| `examples/langsmith_metrics.py` | 18 | [打开精讲](examples--langsmith_metrics_py.md) | [07A](../lessons/07a-eval-observability.md) |
| `examples/live_rag.py` | 52 | [打开精讲](examples--live_rag_py.md) | [03B](../lessons/03b-live-rag.md) |
| `examples/live_variants.py` | 40 | [打开精讲](examples--live_variants_py.md) | [04B](../lessons/04b-rerank-multiquery.md) |
| `examples/load_manuals.py` | 11 | [打开精讲](examples--load_manuals_py.md) | [01B](../lessons/01b-structured-loading.md) |
| `examples/make_demo_pdf.py` | 22 | [打开精讲](examples--make_demo_pdf_py.md) | [02B](../lessons/02b-pdf-tokens.md) |
| `examples/mcp_client.py` | 25 | [打开精讲](examples--mcp_client_py.md) | [09B](../lessons/09b-mcp.md) |
| `examples/mcp_server.py` | 20 | [打开精讲](examples--mcp_server_py.md) | [09B](../lessons/09b-mcp.md) |
| `examples/memory_lifecycle.py` | 17 | [打开精讲](examples--memory_lifecycle_py.md) | [07B](../lessons/07b-memory.md) |
| `examples/pdf_tokens.py` | 25 | [打开精讲](examples--pdf_tokens_py.md) | [02B](../lessons/02b-pdf-tokens.md) |
| `examples/portfolio_snapshot.py` | 25 | [打开精讲](examples--portfolio_snapshot_py.md) | [08B](../lessons/08b-portfolio.md) |
| `examples/retrieval_variants.py` | 16 | [打开精讲](examples--retrieval_variants_py.md) | [04B](../lessons/04b-rerank-multiquery.md) |
| `examples/trace_allowlist.py` | 19 | [打开精讲](examples--trace_allowlist_py.md) | [07A](../lessons/07a-eval-observability.md) |
| `examples/vector_geometry.py` | 21 | [打开精讲](examples--vector_geometry_py.md) | [03A](../lessons/03a-vector-geometry.md) |
| `frontend/client.ts` | 42 | [打开精讲](frontend--client_ts.md) | [05B](../lessons/05b-typescript-ui.md) |
| `frontend/index.html` | 11 | [打开精讲](frontend--index_html.md) | [05B](../lessons/05b-typescript-ui.md) |
| `pyproject.toml` | 30 | [打开精讲](pyproject_toml.md) | [01D](../lessons/01d-cli-tests.md) |
| `src/evidencedesk/__init__.py` | 1 | [打开精讲](src--evidencedesk--__init___py.md) | 包入口阅读 |
| `src/evidencedesk/agnes.py` | 78 | [打开精讲](src--evidencedesk--agnes_py.md) | [03B](../lessons/03b-live-rag.md) |
| `src/evidencedesk/api.py` | 56 | [打开精讲](src--evidencedesk--api_py.md) | [05A](../lessons/05a-api-security.md) |
| `src/evidencedesk/documents.py` | 35 | [打开精讲](src--evidencedesk--documents_py.md) | [01B](../lessons/01b-structured-loading.md) |
| `src/evidencedesk/evaluate.py` | 50 | [打开精讲](src--evidencedesk--evaluate_py.md) | [01E](../lessons/01e-evaluation.md) |
| `src/evidencedesk/hybrid.py` | 43 | [打开精讲](src--evidencedesk--hybrid_py.md) | [04A](../lessons/04a-hybrid.md) |
| `src/evidencedesk/ingest.py` | 27 | [打开精讲](src--evidencedesk--ingest_py.md) | [02A](../lessons/02a-chunks-versions.md) |
| `src/evidencedesk/memory.py` | 30 | [打开精讲](src--evidencedesk--memory_py.md) | [07B](../lessons/07b-memory.md) |
| `src/evidencedesk/search.py` | 55 | [打开精讲](src--evidencedesk--search_py.md) | [01C](../lessons/01c-lexical-search.md) |
| `src/evidencedesk/tickets.py` | 37 | [打开精讲](src--evidencedesk--tickets_py.md) | [06B](../lessons/06b-authorized-tools.md) |
| `tests/test_agnes.py` | 70 | [打开精讲](tests--test_agnes_py.md) | [03B](../lessons/03b-live-rag.md) |
| `tests/test_api.py` | 83 | [打开精讲](tests--test_api_py.md) | [05A](../lessons/05a-api-security.md) |
| `tests/test_core.py` | 97 | [打开精讲](tests--test_core_py.md) | [01E](../lessons/01e-evaluation.md)、[02A](../lessons/02a-chunks-versions.md)、[04A](../lessons/04a-hybrid.md)、[06B](../lessons/06b-authorized-tools.md)、[07B](../lessons/07b-memory.md) |
| `tests/test_integrations.py` | 49 | [打开精讲](tests--test_integrations_py.md) | [02B](../lessons/02b-pdf-tokens.md)、[03A](../lessons/03a-vector-geometry.md)、[06A](../lessons/06a-langgraph.md)、[09B](../lessons/09b-mcp.md) |
| `tests/test_search.py` | 57 | [打开精讲](tests--test_search_py.md) | [01D](../lessons/01d-cli-tests.md) |
| `tests/test_space_export.py` | 12 | [打开精讲](tests--test_space_export_py.md) | [08A](../lessons/08a-deploy-ci.md) |
| `tools/check_course.py` | 42 | [打开精讲](tools--check_course_py.md) | [08A](../lessons/08a-deploy-ci.md) |
| `tools/export_space.py` | 33 | [打开精讲](tools--export_space_py.md) | [08A](../lessons/08a-deploy-ci.md) |
| `tools/fetch_public_manuals.py` | 53 | [打开精讲](tools--fetch_public_manuals_py.md) | [02A](../lessons/02a-chunks-versions.md)、[05C](../lessons/05c-postgres-cache.md) |
| `tools/local_postgres.py` | 57 | [打开精讲](tools--local_postgres_py.md) | [05C](../lessons/05c-postgres-cache.md) |
| `tools/postgres_lab.py` | 100 | [打开精讲](tools--postgres_lab_py.md) | [05C](../lessons/05c-postgres-cache.md) |
| `tools/sync_course_sources.py` | 41 | [打开精讲](tools--sync_course_sources_py.md) | [08A](../lessons/08a-deploy-ci.md) |

## 配置与长期维护

- [10份补充配置/依赖锁讲解](configuration-maintenance.md)：忽略规则、来源清单、前端构建、数据库依赖与锁文件。
- [机器可读覆盖清单](manifest.json)：源码SHA256、物理行数、逐行锚点列表；**不是学习成绩单**。
- [修改源码后怎样同步](maintenance.md)：全文、具体解释、行号、测试证据需要一起复核，不能只刷新hash。
- [本轮验证与未运行项](validation.md)：本地实测、远端发布、教学进度分开记。
