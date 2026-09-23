# 给接手本仓库的 AI 助手

这是一个**一对一辅导中的学习项目**，不是待交付的产品代码库。接手前请先读：

1. **[skills/evidencedesk-tutor/SKILL.md](skills/evidencedesk-tutor/SKILL.md)** —— 学习者偏好的教学方式与归档协议（硬约束）。
2. [README](README.md) 顶部"当前进度"，以及"当前学习"链接指向的那一课：头部 `学习进度：` 一行 + 文末最后一个 `NX-Qn`。
3. [docs/course/regression-cases.md](docs/course/regression-cases.md) —— 未解决的 q06/q09，不得声称已修复。
4. [第二阶段时用户与助手对话部分记录.md](第二阶段时用户与助手对话部分记录.md) —— 真实对话样本，语气与节奏以它为准。

核心规则一句话：**每条消息一个小示例 + 逐行讲差异 + 一个即兴的单题；答后先判定再补充/纠错；把题、原话、标准答案写回教材并推送；不重新开课，不跨阶段自动推进。**

工程约束：所有修改在当前 `arena/*` 工作分支上提交推送，不改 main；改动文档后运行 `python tools/check_course.py`；不为让题目通过而修改金标准、题集或生产实现。
