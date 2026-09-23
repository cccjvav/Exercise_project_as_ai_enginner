# 5D · 集成：真实身份、PostgreSQL 与模型 token 流/取消

[全部课程](../course/index.md) · [上一课](05c-postgres-cache.md) · [下一课](06a-langgraph.md)

- **状态：** 规划中（2026-09-23 修订新增，见[修订记录](../course/course-revision-2026-09-23.md)）。完整示例与逐行讲解在进入本课前由导师补齐。
- **前置理解：** 5A 的服务端身份与 SSE；5B 的取消与安全展示；5C 的 RLS 与缓存键；3C/4C 的主线 API
- **验证状态：** 当前身份是公开固定演示令牌；文档与 ACL 写死在 `api.py`；SSE 只发两帧，不是模型流；PostgreSQL 只在 5C 实验脚本里验证过 documents RLS。
- **节奏：** 建议 3 次：身份 → 数据库 → 流式与取消。
- **学习规则：** 演示令牌替换前不得导入任何真实资料；RLS 测试用实际应用角色，不用管理员。

## 1. 问题：现在为什么需要它？

到这里主线 API 已经能回答，但身份是假的、权限写在代码里、数据在文件里、回答一次性返回。多人产品的最低要求：身份由服务端验证，可见范围来自数据库，模型输出边生成边显示，用户离开时停止计费。

## 2. 原理：在这个问题里理解技术

- **认证与授权分开：** JWT/OIDC 验证"你是谁"（签名、过期、受众）；数据库里的 ACL 与 RLS 决定"你能看什么"。模型永远不参与这一步。
- **请求内的身份传递：** 应用以可信身份设置 PostgreSQL 会话变量 → RLS 生效；事务结束清理；连接池不能串用身份（对应 [集成合同](../course/integration.md) 第 3 项）。
- **流式与取消：** 模型 token 逐帧写入 SSE；浏览器 `AbortController` 断开时，服务端要把取消传播到模型请求，而不是继续消耗配额。
- **缓存键包含用户/授权版本/索引版本**（5C），撤权后旧结果不能再命中。

## 3. 完整示例与逐行讲解

待编写。计划提供：

- `src/evidencedesk/auth.py`：JWT 验证依赖；开发环境用本地签发的测试令牌，不用固定字符串。
- `deploy/schema.sql` 扩展：`documents`、`chunks`、`acl`、`sessions`；应用角色与 RLS 策略。
- `api.py`：`/api/answer` 改为异步流式；文档与 ACL 从 PostgreSQL 读取；`/api/search` 仍保留。
- `frontend/client.ts`：逐帧渲染与取消按钮（保持最小页面，目标岗位为后端）。
- 首次出现 `async def`/`await`/异步生成器时，导师先插入 15 分钟微课。

## 4. 跟着运行与关键实操

1. 用错误签名、过期、正确三种令牌请求 `/api/answer`，观察 401/403/200。
2. 以 Bob 身份请求 Alice 的文档；在数据库层面用应用角色直接 `SELECT`，确认 RLS 与 API 结果一致。
3. 开始一个长回答后在浏览器取消；在服务端日志确认模型请求被中止，用量不再增长。
4. 撤销 Alice 对某文档的权限后再问同一问题，确认缓存不命中、检索不可见。

**闭卷小实现（10–20 行）：** 实现 `cache_key(user, acl_version, index_version, question) -> str`（5C 规则），以及 `claims_valid(claims, now, audience) -> bool`；导师给测试。

## 5. 验证与排错

- 双向越权、撤权、无效令牌、关闭演示模式四组用例全部有自动测试。
- 取消传播有测试或至少一次可复现演练记录（截图/日志去敏）。
- 云端托管数据库（如 Neon Free）只在学习者本人账户下创建，连接串放 Secrets。

## 6. 反思与本课产出

**反思：** 为什么"先全库检索再让模型只引用有权限的文档"是错的？举出一个泄露路径。

**产出：** 可信身份的主线 API、PostgreSQL 承载的文档与权限、流式且可取消的回答、威胁模型草稿。

## 卡住时按需查阅

- https://fastapi.tiangolo.com/advanced/security/
- https://www.postgresql.org/docs/current/ddl-rowsecurity.html
