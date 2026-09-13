# 教材与示例验证记录

日期：2026-09-13。记录的是**导师参考实现的技术验证**，不是学习者已掌握或生产验收通过。

## 已运行

环境：Linux、Python 3.11；精确 Python 依赖见仓库 `requirements-tested.lock.txt`，TypeScript 由 `frontend/package-lock.json` 固定。

| 验证项 | 实际结果 | 范围与限制 |
|---|---|---|
| `python -m pytest -q` | **63 passed** | 含核心、API、Qdrant、LangGraph、MCP 和 PDF 文本提取；不调用在线模型 |
| `npm --prefix frontend ci --ignore-scripts` / `npm --prefix frontend run build` | 安装/编译通过 | 不等于真实浏览器端到端交互验收 |
| 检索基线 k=1/3 | Recall=MRR=5/6；无答案空返回率=1 | 仅 8 条公开开发题，q06 有隐含 Webhook 上下文 |
| Qdrant | 内存 collection、查询、租户过滤通过 | 向量为手工几何夹具，不是语义模型效果 |
| LangGraph | 暂停后批准、拒绝、非布尔拒绝通过 | 只有内存 checkpoint，未测跨进程数据库恢复 |
| 工单 | 未审批/越权/改草稿拒绝；重试与文件数据库重开幂等通过 | SQLite 模拟，不是外部 API exactly-once 保证 |
| MCP | stdio 初始化、发现与工具调用通过 | 只读公开虚构资料，无远程鉴权 |
| PDF | 生成虚构 PDF、提取文本、空页明确报错通过 | 不提供 OCR，不保证真实 PDF 的阅读顺序 |
| Agnes adapter | dry-run 与 14 项模拟请求/引用/预算保护测试通过 | 无真实模型调用；不能当答案效果证明 |
| PostgreSQL 18.4 | 6 份文档入库、非超级用户双向隔离、越权 INSERT/UPDATE 拒绝、事务身份清理与重启读取通过 | 仅本地 documents RLS；未验证托管数据库与应用认证 |
| 免费展示包 | 23 个白名单文件导出并测试；当前工作区 HTTP 预览可用 | 未上传 HF，未运行 Docker 构建；预览不是永久部署 |
| 课程校验 | 22 节、源码副本、本地链接、Python 语法 | 不自动核验外部链接或在线供应商 API |

pytest 当前有一条 Starlette/AnyIO 的弃用警告，不影响用例通过；后续升级需检查兼容性，不隐藏警告。

## 预览 401 修正

用户反馈预览页面请求全部 401；服务器日志确认代理来源请求连续 401，而本机带 Bearer 演示令牌为 200。当前最可疑的是预览链路对 Authorization 的处理，**尚未直接观测真实代理如何更改该头**。浏览器已改用 X-Demo-Token，后端仅在显式演示模式下校验固定令牌；保留旧 Bearer CLI，不关闭身份/ACL 校验。新增模拟剥离 Authorization、无效令牌、双向 ACL 和关闭演示模式测试；模拟通过不能替代用户实际浏览器复测。已重新编译并重启预览，脚本 URL 带新版本以避开旧缓存。

## 已发现的阻塞，不伪装为成功

`tiktoken.get_encoding("cl100k_base")` 首次下载编码表时，本环境到 `openaipublic.blob.core.windows.net` 出现 TLS 连接关闭错误。我们没有关闭 TLS 校验绕过。PDF 提取/空页路径已测，完整 token 计数路径仍待网络可用后验证。

工作区访问 Debian 软件源和 Hugging Face 模型下载还存在 TLS/连接限制。PostgreSQL 本轮改用固定版本第三方 npm 二进制包，在隔离的 Unix socket 上完成真实验证。Agnes API 无密钥连通性检查也返回 ConnectError；完整在线生成仍待安全授权和可用网络。细节见 [零预算方案](zero-budget.md)。

## 未执行或未完成

- 在线 OpenAI embedding/chat、Ragas 裁判、托管 LangSmith 上传、Deep Agents 付费运行。
- sentence-transformers/BGE/cross-encoder 下载与真实多查询重排序效果；相应脚本是完整参考，但未运行。
- Deep Agents / Ragas 的额外安装组合未做环境兼容验收；不要因为语法校验通过就称 API 已验证。
- 托管 PostgreSQL、tickets RLS、真实应用身份联动、Redis 真实连接、持久化图状态（本地 documents RLS 已完成验证）。
- Docker 镜像构建/运行：当前工作区没有 Docker 命令；提供文件和清晰的本机操作步骤。
- 云部署、真实 OIDC/JWT、真实工单 API、浏览器交互 E2E、负载/安全审计。
- GitHub Actions 远端状态须在推送后到仓库检查；本地通过不代表远端已完成。

## 复现已测试的部分

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-tested.lock.txt
python -m pip install --no-deps -e .
npm --prefix frontend ci --ignore-scripts
npm --prefix frontend run build
python -m pytest -q
python tools/check_course.py
python -m evidencedesk.evaluate --k 1
python -m evidencedesk.evaluate --k 3
```

Windows 使用对应虚拟环境激活命令。首次安装/下载需要网络；依赖快照仅代表当前测试平台，不是所有系统的保证。

新增学习改动后重新执行，而不是沿用本页数字。未经执行的课程实操标待验，进度由导师与你共同确认。
