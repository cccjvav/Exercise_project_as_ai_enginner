# 零预算执行方案：免费模型、真实数据库与云部署

核实日期：**2026-09-13**。免费政策会改变，以具体模型、账户和当日后台为准。本轮没有购买任何资源、充值、升级套餐或调用付费模型。“零费用”指本项目不额外购买模型 API/云资源，不替 Arena 平台或你本机电费作承诺。

## 先给结论

| 项目 | 现在的方案 | 本轮实际状态 |
|---|---|---|
| 生成模型 | Agnes `agnes-2.5-flash` 当前免费价格；需要账户权益确认 | 已完成保守接入与模拟测试，**未真实调用** |
| 检索 | 先用已有本地词法/BM25，不强制购买 OpenAI embedding | 已运行；不冒充中文语义模型 |
| 关系数据库 | 当前工作区真实 PostgreSQL 18.4 | **已启动、入库、RLS 与重启持久化验证通过** |
| 真实资料 | FastAPI 官方仓库的 3 份 MIT 文档 | **已下载、固定版本、保留许可证与校验摘要** |
| 在线临时展示 | Arena 当前工作区预览 | **已启动；不等于独立长期云部署** |
| 独立免费展示 | Hugging Face Docker Space / CPU Basic | **部署包已生成；未创建或上传到你的账户** |
| 托管 PostgreSQL | Neon Free 可作为后续选择 | **已核实免费来源；未创建云数据库** |

教材里的 OpenAI 是一个参考接入示例，不是必须付费才能学下去。你可以完成整个主线的理解与离线实验，再按实际免费额度验证模型。

## 1. 免费模型到底怎么选？

### 首选：你提到的 Agnes AI

我核对了[官方模型页](https://agnes-ai.com/en/docs/agnes-25-flash)与[价格页](https://agnes-ai.com/en/docs/pricing)。当前 `agnes-2.5-flash` 输入、输出价格列为 0；但其他型号有收费项，官方也提醒实际价格取决于账户权益和促销阶段。因此：

- 只考虑后台明确显示免费的 **`agnes-2.5-flash`**，不自动换 Pro/Beta。
- 只用免费 Key/免费额度，不订阅 Token Plan、不充值、不启用付费后备模型。
- 限额用完就停止，收到 402/429 不自动升级、充值或无止境重试。
- 不承诺它永远免费、无调用限制或特定效果达标。

官方接入地址为 `https://apihub.agnes-ai.com/v1/chat/completions`，使用 Bearer API Key。[接入文档](https://agnes-ai.com/en/docs/quickstart)

**当前双重阻塞：** 尚未获得你账户的明确调用授权/安全配置；且工作区对该 API 的无密钥连通性检查返回 ConnectError。即使配置 Key，也不能先承诺这里一定连得通。可在你的本机或已授权的 Hugging Face 环境再次检查，不关闭 TLS 验证，也不绕过供应商地区/账户限制。

### 仓库已经提供的保守示例

- `src/evidencedesk/agnes.py`：固定供应商地址和型号；不会把 key 发到用户提供的网址。
- `examples/agnes_rag.py`：默认 **dry-run，零网络调用**。
- 一次最多请求一次，输出上限 400 token；无自动重试、重定向或付费后备模型。
- 只检索仓库内虚构资料，不接受任意文件路径。
- JSON 与引用校验失败就停，不再额外花调用来“修复答案”。
- 没有公开 HTTP 模型接口，避免别人消耗你的免费配额。

```bash
python -m pip install -e ".[web]"
python -m examples.agnes_rag
python -m pytest tests/test_agnes.py -q
```

默认会显示 dry-run、候选文档、型号与请求上限，不会生成一份假答案。

### 真正调用前，你只需要做的动作

1. 在[Agnes 官方平台](https://platform.agnes-ai.com/)注册/登录自己的账号。
2. 查看具体 `agnes-2.5-flash` 的价格、免费权益、API Key 类型与额度。若出现付费要求就停下，不要为了课程买套餐。
3. 生成自己的 API Key，**不要发到聊天、截图或提交到 Git**。
4. 在你能控制的本机终端用隐藏输入临时配置，或使用宿主平台的 Secrets（不是公开 Variables）：

```bash
# Bash 本机交互终端，输入内容不会显示；这不是让你把 Key 发给导师。
read -rs AGNES_API_KEY
export AGNES_API_KEY
python -m examples.agnes_rag --live --confirmed-current-free
unset AGNES_API_KEY
```

Windows 可使用 IDE/系统凭据工具配置当前进程环境。脚本不自动加载 `.env`。若 Arena 没有安全环境变量入口，就先在你本机运行，不通过聊天传 Key。

5. 运行后对照原文人工检查答案；把**不含密钥的结果/错误类型**告诉导师即可。模拟接口测试通过不代表真实模型已经验证。

上限标记不是账单硬限制；免费政策变化时必须停止并重新确认。没有 Key 或连不通也不会阻止你学习数据库、API、测试和部署。

### 其他零预算选择

- **Groq Free Plan：** 官方有按模型区分的请求/token 限额，超限返回 429；账号控制台显示实际额度。它可作为聊天模型备选，不应假设也提供你需要的 embedding。[5](https://console.groq.com/docs/rate-limits)
- **Gemini API：** 官方列出 Free tier，支持地区包括丹麦；但是否能用某型号仍需账户确认，不要把网页聊天免费等同于 API 所有模型免费。[1](https://ai.google.dev/gemini-api/docs/available-regions) [4](https://ai.google.dev/gemini-api/docs/billing)
- **本地开源模型：** 可以避免按 token 收费，但需下载权重、满足许可证、RAM/磁盘和计算条件。当前工作区约 4GB RAM，不适合直接把大模型全装进来；到 Hugging Face 的直接下载也遇到 TLS 错误。后续可根据你电脑配置选小型模型或本地 embedding，而不是先要求你买 GPU。

## 2. “真实数据库”与“真实资料”不是同一件事

- **数据库系统**：真正运行 PostgreSQL，执行 SQL、事务和权限策略。并不要求付费，也不要求带真实客户数据。
- **资料来源**：放进数据库的文本。可以是虚构手册，也可以是许可清楚的公开资料；不应寻找未经授权的企业内部数据。

### 本轮真正运行了什么？

- PostgreSQL 18.4 服务，**不是 SQLite 替身或 SQL 模拟器**。
- 仅监听权限为 0700 的本地 Unix socket，禁用数据库 TCP 监听，不对公网开放数据库端口。
- 初始管理员只用于初始化；RLS 检查用 `NOSUPERUSER NOBYPASSRLS` 的非表所有者角色。
- 导入 6 份文档：alpha 租户的 3 份虚构手册、beta 的 3 份真实公开文档。
- 验证双向租户读取隔离、越权 INSERT/UPDATE 被拒、事务结束身份设置清理。
- 停止服务再启动，持久化的验收记录仍可读取。

日志里的 RLS 拒绝错误是测试**预期结果**，不是运行失败。测试临时表/角色会清理，仅留下小型验收凭据。这里只验证 `documents` 表，不能据此宣称 `tickets`、应用身份和所有业务表都已安全。

应用负责从可信身份设定租户 GUC；RLS 不能保护“把原始 SQL 或 set_config 权限随意交给最终用户”的错误架构。`SET LOCAL ROLE` 用于测试实际有效权限，不是生产认证实现。

### 安装来源及本机复现

当前工作区访问 Debian 软件源失败，因此没有偷偷关闭 TLS；改用 npm 分发的固定版本 **第三方 PostgreSQL 二进制包**。包版本和完整性摘要记录在 `tools/postgres-runtime/package-lock.json`。它不是 PostgreSQL 官方安装包，仅用于隔离的课程实验；生产应使用受审计的官方发行或托管服务。

```bash
# 本方案仅支持当前 Linux x64 工作区；Windows/macOS 不照抄此二进制安装。
npm --prefix tools/postgres-runtime ci --ignore-scripts
python -m pip install -r requirements-database.txt
python tools/local_postgres.py version
python tools/local_postgres.py init
# 在一个终端运行服务（Arena 中由进程工具管理，不使用 nohup/后台 bash）：
python tools/local_postgres.py serve
```

另一个终端运行：

```bash
python tools/fetch_public_manuals.py
python tools/postgres_lab.py
# 服务正常停止并重启后：
python tools/postgres_lab.py --check-persisted
```

`init` 不覆盖已有数据库。仅生成 `artifacts/postgres/` 下的实验数据，Git 忽略；工作区重建后需要重新初始化/下载，**不要把这个临时工作区当长期托管数据库**。

### 你要找的公开资料来源

选择了 [FastAPI 官方仓库](https://github.com/fastapi/fastapi)，并实际取得其 MIT 许可证。

| 文档 | 内容 | 适合什么练习 |
|---|---|---|
| Deployment Concepts | 部署、运行、内存、进程 | 长文分块、运维知识检索 |
| About HTTPS | HTTPS 与证书/代理概念 | 引用、条件与术语 |
| Security First Steps | 安全与身份入门 | 开发者支持问答 |

固定提交：`50113da16fec53b66b80d75e80a89296de4fa5a5`。清单在 `data/sources/fastapi.json`，下载脚本保存原文、SHA256、来源和 LICENSE.txt；实际下载正文约 41.6KB。原文/处理结果放在 Git 忽略的 `data/raw/` 和 `data/processed/`。

这些是英文开放文档，不是 Northstar Cloud 的真实企业政策。它们作为独立语料，不能把原有 8 条虚构手册题集直接用来算其准确率。后续需建立自己的相关性标签；文档模板代码/缺失 include 也需在正式入库前清洗。

### 真正的免费云端 PostgreSQL 来源

建议先考虑 **Neon Free**。官方介绍当前免费计划无需信用卡，包含每项目 0.5GB 存储和每月 100 CU-hours，达到限额会暂停，适合小型学习原型。[3](https://neon.com/faqs/managed-postgres-databases-free-tier)

本轮**没有创建 Neon 资源**。需要由你长期管理时，先在 [Neon 官方站点](https://neon.com/pricing)建立自己的 Free 账户，不升级。数据库连接串包含密码，只放应用宿主的 Secrets，不发聊天。连云端时启用供应商要求的 TLS；不要把它直接放进浏览器 JS。

## 3. 云部署，用最直白的话解释

- **在你电脑运行**：电脑开着且程序运行时能用。
- **当前 Arena 预览**：程序在这次工作区运行，提供一个浏览器入口；工作区停了，预览可能也停。
- **独立云部署**：把程序交给另一个服务平台运行，得到独立网址，不依赖当前 Arena 会话。免费服务也可能休眠，并非永远在线。

目前你可以点 **「EvidenceDesk · 零模型费用演示」** 预览。已实际检查 HTTP 健康接口、正常检索和用户隔离。页面仍只使用虚构手册、词法检索；**它还没有把 PostgreSQL 和 Agnes 连接成完整产品**。

### 推荐的第一步：Hugging Face Spaces 免费 CPU

官方 Spaces 说明默认免费资源包含 2 CPU 核、16GB RAM 和非持久磁盘；免费硬件闲置会休眠。[3](https://huggingface.co/docs/hub/spaces-overview?amp=&amp=)

我们先部署**不调用模型、不连接外部数据库的演示**，这样不需要将任何 API Key 放到公网应用，也不会让访客消耗模型配额。看懂部署后，再分别连接数据库和模型。

### 已生成部署包，但没有上传

```bash
python tools/export_space.py
# 输出 artifacts/evidencedesk-space.zip
```

只打包白名单内的 23 个小型源码/配置文件，不包含 `.env`、Git 凭据、模型权重、PostgreSQL 数据、第三方公开文档或其它原始数据。已检查压缩包内容；**尚未运行 Docker 构建，也没有替你注册/上传云账户**。

### 你在网页上按这几步操作

1. 在 [Hugging Face](https://huggingface.co/join)注册/登录自己的账号。
2. 打开 [Create a new Space](https://huggingface.co/new-space)，起名如 `evidencedesk-demo`。
3. SDK 选择 **Docker**，硬件选 **CPU Basic / Free**。不选 GPU、不购买存储；若提示必须付费则先停止。
4. 下载并在本机解压 `artifacts/evidencedesk-space.zip`。在 Space 的 Files 页面上传解压后的文件和文件夹，**保持根目录有 Dockerfile、README.md、pyproject.toml 等**。不是把 zip 当成应用文件直接上传。也可用官方 Web/CLI 上传目录，保持相同层级。
5. 在 Settings → Variables 添加 `EVIDENCEDESK_DEMO`，值为 `1`。这是公开演示开关，不是密钥；本包无需任何模型 Secret。
6. 等待构建。在 Logs 中查看依赖安装、前端编译和 uvicorn 是否成功启动。
7. 打开 App，正常搜索“Webhook 重试多少次？”，再切换用户观察权限差异。
8. 若失败，发**去敏后的构建错误与公开 Space 地址**给导师。不要发 HF token 或账户登录凭据。

Docker Space 的端口在 README 的 YAML `app_port` 与服务监听端口中一致配置；本包使用 8000，并非必须固定 7860。[Docker Spaces 官方说明](https://huggingface.co/docs/hub/spaces-sdks-docker)

公开固定令牌只展示虚构资料。**不要在未做真实认证/限流之前，将 Agnes 调用加进这个公开接口。** 未来模型 Key 放 Secrets，数据库用托管服务，不把免费 Space 的临时磁盘当永久 PostgreSQL 存储。

## 4. 接下来只做一个动作即可

你不需要同时弄懂三个平台。建议先选：

- 想先验证生成答案：在 Agnes 后台确认 `agnes-2.5-flash` 免费权益，只告诉导师“已确认/没找到”，不要发 Key；然后我们带着做安全配置与单次调用。
- 想先理解部署：先创建 Hugging Face 的免费 Docker Space，上传无密钥演示包；把公开地址或去敏错误告诉导师。

数据库原理和真实 PostgreSQL 验证已经可以继续学习，不需要先开通付费数据库。
