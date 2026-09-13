# 8A · Docker、依赖快照与 CI

[全部课程](../course/index.md) · [上一课](07b-memory.md) · [下一课](08b-portfolio.md)

- **前置理解：** 阶段 7；Node.js 22、Python 3.11；Docker 为本地可选前提
- **验证状态：** 本机测试和 TS 构建已运行；当前环境无 Docker，镜像/云部署与 GitHub 远端检查另行验收。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

> 新增 [Hugging Face 免费 CPU 的网页部署步骤与导出包](../course/zero-budget.md)，当前工作区预览已启动，独立云端上传仍待你的账号操作。

## 1. 问题：现在为什么需要它？

演示依赖你的电脑状态，就不能作为可复现作品。我们把运行环境、构建命令和测试门槛写进文件，并区分服务活着与业务可用。

## 2. 原理：在这个问题里理解技术

多阶段 Docker 先编译前端再复制静态文件；非 root 运行降低权限。镜像明确 COPY 需要的路径，不将 .env 和原始资料打包。health 是活性检查，本例无外部依赖，不能证明真实模型/数据库可用。

CI 在无密钥环境运行确定性测试；安装快照复现已测试依赖，模型调用不默认进入 PR 检查。Python 快照对应当前平台而非带哈希的全平台锁，升级需独立环境验证；生产还需审查依赖供应链与镜像摘要。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `deploy/Dockerfile`

完整源文件：[打开源码](../../deploy/Dockerfile)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: deploy/Dockerfile -->
```dockerfile
#: 前端构建阶段只用于编译；最终镜像不携带 node_modules。
FROM node:22-bookworm-slim AS frontend
WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci --ignore-scripts
COPY frontend/ ./
RUN npm run build

#: 复制明确的课程运行文件，不把 .env、Git 或原始数据打包进去。
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml requirements-tested.lock.txt ./
COPY src/ ./src/
COPY data/sample/ ./data/sample/
COPY --from=frontend /web/index.html /web/client.js ./frontend/
RUN pip install --no-cache-dir -r requirements-tested.lock.txt && pip install --no-deps -e .
#: 非 root 运行；对外绑定 0.0.0.0，浏览器请求仍使用同源相对路径。
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"
CMD ["uvicorn", "evidencedesk.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–8 | 前端构建阶段只用于编译；最终镜像不携带 node_modules。 |
| 9–16 | 复制明确的课程运行文件，不把 .env、Git 或原始数据打包进去。 |
| 17–22 | 非 root 运行；对外绑定 0.0.0.0，浏览器请求仍使用同源相对路径。 |

### `.github/workflows/course.yml`

完整源文件：[打开源码](../../.github/workflows/course.yml)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: .github/workflows/course.yml -->
```yaml
#: 8A：只跑无密钥测试；pull_request 不获得生产密钥或模型费用权限。
name: Course checks
on: [push, pull_request]
#: 最小权限只读仓库；测试不需要向 GitHub 或生产服务写入。
permissions:
  contents: read
jobs:
  offline:
    runs-on: ubuntu-latest
    steps:
      #: 按当前提交检出并固定 Python/Node 主版本；生产可进一步固定 action 提交摘要。
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      #: 先安装已测试依赖快照，再注册本地包；前端使用 npm lock 复现编译。
      - run: pip install -r requirements-tested.lock.txt && pip install --no-deps -e .
      - run: npm --prefix frontend ci --ignore-scripts && npm --prefix frontend run build
      #: 不调用在线模型；本地源码同步检查防止教材示例与实际实现漂移。
      - run: python -m pytest -q
      - run: python tools/check_course.py
      - run: python -m evidencedesk.evaluate --k 1
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–3 | 8A：只跑无密钥测试；pull_request 不获得生产密钥或模型费用权限。 |
| 4–10 | 最小权限只读仓库；测试不需要向 GitHub 或生产服务写入。 |
| 11–18 | 按当前提交检出并固定 Python/Node 主版本；生产可进一步固定 action 提交摘要。 |
| 19–21 | 先安装已测试依赖快照，再注册本地包；前端使用 npm lock 复现编译。 |
| 22–25 | 不调用在线模型；本地源码同步检查防止教材示例与实际实现漂移。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m pip install -r requirements-tested.lock.txt
python -m pip install --no-deps -e .
npm --prefix frontend ci --ignore-scripts
npm --prefix frontend run build
python -m pytest -q
python tools/check_course.py
# 本机安装 Docker 后，以下仅部署公开虚构演示
docker build -f deploy/Dockerfile -t evidencedesk:course .
docker run --rm -p 8000:8000 -e EVIDENCEDESK_DEMO=1 evidencedesk:course
```

### 只做这些关键改动

1. 在独立虚拟环境按命令复现，不覆盖你其他项目环境。
2. 有 Docker 时构建并启动，在 /health 和页面检索各验证一次。
3. 停掉容器，按同样镜像重启；当前应用从手册重载，工单/记忆示例未接入这个服务，不应期待它们持久化。
4. 推送自己的学习改动后查看 Actions 实际结果；未运行或红灯必须如实记录，不能用本地通过代替远端通过。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

无密钥测试、TS 编译、课程链接检查应通过。浏览器请求使用相对 URL；0.0.0.0 用于服务监听。Dockerfile 中健康检查访问容器自身 localhost 合理，与浏览器访问远端后端不同。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 部署到云前需要确认哪些费用、密钥、TLS、日志、备份、限流和回滚要求？为什么本课程不自动替你创建付费资源？

**产出：** 可审查 Dockerfile、CI 文件、复现记录与待执行部署清单。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://docs.docker.com/build/building/multi-stage/
- https://docs.github.com/en/actions

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。
