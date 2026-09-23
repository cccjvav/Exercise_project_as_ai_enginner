# 6C · 集成：工单流经 API（草稿、审批、幂等、审计）

[全部课程](../course/index.md) · [上一课](06b-authorized-tools.md) · [下一课](07a-eval-observability.md)

- **状态：** 规划中（2026-09-23 修订新增，见[修订记录](../course/course-revision-2026-09-23.md)）。完整示例与逐行讲解在进入本课前由导师补齐。
- **前置理解：** 6A 的 interrupt/恢复；6B 的审批哈希、幂等键、参数校验；5D 的真实身份与 PostgreSQL
- **验证状态：** `approval_graph.py` 与 `tickets.py` 是独立脚本，checkpoint 在内存，工单在 SQLite，审批对象由脚本构造，尚未经过任何 API。
- **节奏：** 建议 3 次：持久化 checkpoint 与审批记录 → API 端点 → 失败路径演练。
- **学习规则：** 客户端自报 `approved=true` 永远不可接受；先接模拟外部系统，真实工单系统另行申请。

## 1. 问题：现在为什么需要它？

6A/6B 证明了机制，但真实风险出现在边界：谁能恢复哪个 thread、审批记录存在哪、重试来自浏览器还是网络、审批后草稿被改了怎么办。这些只有把流程放进 API 和数据库才会暴露。

## 2. 原理：在这个问题里理解技术

- **thread 归属由服务端映射：** `thread_id` 与用户/租户绑定在数据库中；恢复请求先校验归属（对应 [集成合同](../course/integration.md) 第 4 项）。
- **审批记录是受保护数据：** 含草稿哈希、审批人角色、时效、状态；工具执行时从存储加载并重新校验，而不是信任图状态里的字段。
- **幂等键的来源：** 由服务端在草稿创建时生成并返回给客户端；同键同内容返回原结果，同键不同内容报冲突。
- **审计：** 每次拒绝、批准、执行、冲突都留下可查询记录，不含密钥与客户原文。

## 3. 完整示例与逐行讲解

待编写。计划提供：

- `deploy/schema.sql` 扩展：`approvals`、`tickets`、`audit_log`，含 RLS。
- LangGraph 持久化 checkpointer（PostgreSQL），`approval_graph.py` 迁入 `src/`。
- `api.py`：`POST /api/tickets/draft`、`POST /api/tickets/{thread}/approve`（需审批角色）、`POST /api/tickets/{thread}/execute`。
- 模拟外部工单 API（本地 FastAPI 子应用），可注入超时与 5xx。

## 4. 跟着运行与关键实操

1. 以普通用户创建草稿；以同一用户尝试批准，预期被拒；以审批角色批准。
2. 批准后修改草稿再执行，预期哈希不匹配被拒，需要重新审批。
3. 执行时让模拟外部 API 超时，再重试同一幂等键；确认只创建一张工单。
4. 以另一租户用户恢复该 thread，预期 403，且错误信息不泄露草稿内容。

**闭卷小实现（10–20 行）：** 实现 `can_execute(approval_row, draft_hash, actor, now) -> tuple[bool, str]`，返回是否允许与拒绝原因（不存在/过期/撤销/哈希不符/角色不符/跨租户）；导师给测试。

## 5. 验证与排错

- 拒绝、不存在、过期、撤销、内容变化、跨用户六类审批失败都有测试。
- 服务重启后未完成的 thread 能恢复；重复执行不重复创建。
- 审计表能回答"这张工单是谁在何时基于哪个草稿哈希批准的"。

## 6. 反思与本课产出

**反思：** 为什么这个流程不需要模型自主决定下一步？哪一步如果交给模型会造成什么后果？

**产出：** 经 API 与数据库的完整工单流、失败路径测试、审计查询示例。

## 卡住时按需查阅

- https://docs.langchain.com/oss/python/langgraph/persistence
- [集成合同](../course/integration.md)
