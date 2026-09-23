# 3C · 集成：/api/answer（分块 → 向量 → 免费模型 → 引用校验）

[全部课程](../course/index.md) · [上一课](03b-live-rag.md) · [下一课](04a-hybrid.md)

- **状态：** 规划中（2026-09-23 修订新增，见[修订记录](../course/course-revision-2026-09-23.md)）。完整示例与逐行讲解在进入本课前由导师补齐。
- **前置理解：** 3A 的向量几何与 Qdrant；3B 的结构化输出与引用校验；2C 语料已建立；免费 API 已在本机连通
- **验证状态：** 当前 `api.py` 只有词法 `/api/search`，读文件、无分块、无向量、无模型。
- **节奏：** 建议 3 次：把 2A 的块写进 Qdrant → 接模型 → 接到 FastAPI。
- **学习规则：** 保留 `/api/search` 作为确定性对照；LLM 失败要返回可诊断错误，不能伪装成"没有答案"。

## 1. 问题：现在为什么需要它？

3A/3B 各自是脚本，每次重建内存索引、整篇文档喂模型。真正的产品链是：块 → 向量（带父 ID、版本、来源、租户）→ 服务端身份过滤 → 检索 → 证据充分性 → 生成 → 引用校验 → 展示。本课把这条链第一次接通，之后每个阶段都往这条主线上加东西，而不是再写新脚本。

## 2. 原理：在这个问题里理解技术

- **索引与查询用同一 embedding 模型与版本**；payload 携带 `chunk_id / parent_id / version / source / tenant`，回答时先按 `parent_id` 映射回文档级评测。
- **活动索引版本指针：** 新语料或新分块参数生成新 collection，验证通过再切换；失败不切换（对应 [集成合同](../course/integration.md) 第 1 项）。
- **引用校验是程序能做的最低限度：** ID 必须来自本次证据集合；`insufficient_evidence=true` 时引用为空；"引用存在但不支持结论"仍需人工/评测发现。
- **错误分层：** 供应商 4xx/5xx、超时、限额、格式不合约定、引用不一致，各自返回不同的可诊断错误码；不用重试或换模型"修复答案"。

## 3. 完整示例与逐行讲解

待编写。计划提供：

- `src/evidencedesk/index.py`：从 2A 的 `chunks()` 构建 Qdrant collection，payload 含身份字段；活动版本指针。
- `src/evidencedesk/answer.py`：`answer(question, tenant, k) -> Answer`，内部为检索 → 提示 → 结构化输出 → 引用校验；模型客户端通过 `base_url` 指向任一 OpenAI 兼容接口。
- `api.py` 新增 `POST /api/answer`；`/api/search` 保留。
- `tests/test_answer.py`：用假模型（transport 注入）测试引用不一致、拒答、供应商错误分层，不需要密钥。

## 4. 跟着运行与关键实操

1. 用 2C 语料建立向量索引，打印 collection 大小与向量维度；改分块参数生成第二个版本，切换活动指针。
2. 通过 `/api/answer` 分别问一道精确题、一道换说法题（含 q06b）、一道有关键词无答案题（q09）；逐项人工核对答案与引用原文。
3. 故意让模型返回不存在的引用 ID（用假模型），观察 API 返回的错误码。
4. 记录模型名、日期、延迟、用量到 [回归跟踪](../course/regression-cases.md)；q06/q09 状态如实更新。

**闭卷小实现（10–20 行）：** 实现 `check_citations(answer, allowed_ids) -> None`，按 3B 的四条规则抛出带原因的 `ValueError`；导师给测试。

## 5. 验证与排错

- 无密钥时 `pytest` 全部通过（假模型）；有密钥时单独启用在线用例。
- 跨租户：Bob 问 Alice 才可见的文档，检索前已过滤，证据为空则拒答，且错误信息不泄露不可见标题。
- 在 2C 开发集上跑文档级 Recall@k、MRR、无答案表现，与词法基线并排记录。

## 6. 反思与本课产出

**反思：** 引用 ID 合法、答案流畅、指标上升，三者都成立时你还需要检查什么？举一个"引用存在但不支持结论"的具体例子。

**产出：** 能回答的主线 API、带身份字段的向量索引、第一份真实模型对照记录、q06/q09 的新状态。

## 卡住时按需查阅

- [集成合同](../course/integration.md)
- https://docs.langchain.com/oss/python/langchain/structured-output
