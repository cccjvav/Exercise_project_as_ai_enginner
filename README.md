# EvidenceDesk · 有据可查的企业知识与工单助手

**项目驱动的 AI 工程课程：9 个阶段，22 节小课，教材已提前备齐。**

教学方式：**完整示例 → 逐行讲解 → 预测结果 → 按明确步骤做关键改动 → 验证与反思**。不要求你先从空文件摸索；理解和验收不以默写代码为标准。

## 现在从哪里开始？

- **[零预算方案与本轮实际执行结果](docs/course/zero-budget.md)** — Agnes 免费型号、真实 PostgreSQL、公开资料和逐步云部署。
- **[全部课程目录](docs/course/index.md)** — 22 节完整小课、顺序和阶段验收要求。
- **[当前学习：1C 词法检索](docs/lessons/01c-lexical-search.md)** — 1A、1B 已完成，现在学习怎样挑选候选依据。
- [环境准备与依赖分层](docs/course/setup.md) — 不要一次安装全部框架。
- [实际验证结果与未验证事项](docs/course/verification.md) — 不把未运行内容称为成功。
- [整体项目路线与技术取舍](docs/roadmap.md)。

**当前进度：1A、1B 已完成，1C 进行中。** 提前备齐教材，不代表后续阶段已自动通过；完成一阶段后，导师仍会询问是否继续。

## 要构建什么？

为虚构 SaaS 公司的内部支持团队构建助手：从产品手册和运维流程中找依据，回答附带来源；没有依据时不编造；后续在权限校验、人工审批和幂等保护下协助创建工单。

最终作品目标是可部署、可评测的前后端应用，而非只有聊天界面。技术必须服务问题，不以安装框架数量为成果。

## 教材齐备，不等于生产项目已经完成

当前仓库提供：

- 确定性的文档加载、词法检索、CLI、评测与测试。
- 字符分块/版本、真实 Qdrant 本地几何实验、BM25/RRF 机制示例。
- 可运行的 **FastAPI + TypeScript 词法证据演示**，使用公开固定演示身份，仅限虚构资料。
- LangGraph 暂停恢复、SQLite 模拟工单、记忆生命周期和只读 MCP 实验。
- 完整在线 RAG、真实模型检索对照、Ragas/LangSmith、Deep Agents **参考脚本**；付费/模型下载实验没有冒充已实测。
- Docker/CI 文件、课程源码同步检查、实验与作品集模板。

这些组件**尚未全部集成到一个生产级应用**。真实身份、持久化服务、在线模型效果、云部署和浏览器端到端验收都有明确待办，见 [集成顺序与毕业合同](docs/course/integration.md)。

## 第一课运行

Python 3.11+，无需第三方依赖：

```bash
python examples/01_read_document.py
```

1B 开始才创建虚拟环境并安装基础课程依赖：

```bash
python -m venv .venv
# macOS / Linux；Windows PowerShell 使用 .venv\Scripts\Activate.ps1
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m examples.load_manuals
python -m pytest -q
```

只装 dev 时，可选集成测试会跳过；完整测试环境的命令和记录见验证说明。

## 目录

```text
docs/course/         课程总入口、环境、集成与验证说明
docs/lessons/        22 节小课 + 阶段 1 总览
docs/experiments/    消融实验和作品集模板
docs/reviews/        阶段验收记录模板
src/evidencedesk/    可复用课程组件
examples/            独立教学实验（按需依赖）
tests/               无模型密钥的确定性和本地集成测试
frontend/            TypeScript 源码及 npm lock
deploy/              Dockerfile、PostgreSQL 参考 schema
data/sample/         纯虚构练习资料
data/questions.jsonl 公开开发题，非最终测试集
tools/check_course.py 本地链接、源码同步与语法校验
```

## 协作与安全

- 正确作答后，将原题、学习者回答、标准答案与关键解析归档到对应课程的“已完成问答与标准答案”；不提前填写未答题，不把单题通过记为整阶段通过。

- 导师提供示例和步骤；学习者通过解释、小变式和复现证明理解。明确区分参考代码与本人完成的改动。
- 调试提供命令、完整错误栈、预期和实际，不提供密钥或个人信息。
- 不将真实企业文件直接用于演示；模型调用、追踪和评测外发均需授权及预算确认。
- 不编造指标；fixture 只解释机制，不能当作真实模型效果。
- 所有工作位于 `arena/01a0981c-exercise-project-as-ai-enginne`，不自动修改远程 main。
