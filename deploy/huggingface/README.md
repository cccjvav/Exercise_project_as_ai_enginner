---
title: EvidenceDesk Course Demo
emoji: 📚
colorFrom: teal
colorTo: green
sdk: docker
app_port: 8000
---

# EvidenceDesk · 免费 CPU 课程演示

这是虚构手册的词法证据检索，不是在线模型答案。公开固定演示令牌不适用于真实企业资料。

创建 Space 时选择 **Docker / CPU Basic（Free）**，不要升级硬件、绑定付费服务或购买持久化磁盘。
在 Settings → Variables 添加 `EVIDENCEDESK_DEMO=1`。本演示不需要任何模型密钥。

免费空间可能休眠，容器内磁盘不应视为持久数据库。当前实例不连接工作区 PostgreSQL，也不调用 Agnes。
未来上线私有数据或模型调用前，需要真实身份、服务端限流、额度/预算控制、授权和保留策略。

Source course: https://github.com/cccjvav/Exercise_project_as_ai_enginner/tree/arena/01a0981c-exercise-project-as-ai-enginne
