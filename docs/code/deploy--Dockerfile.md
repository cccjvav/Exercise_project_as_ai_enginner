# 多阶段构建与最小运行入口：逐行精讲

[精讲总目录](index.md) · [对应源码](../../deploy/Dockerfile)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

先用Node编译前端，再用Python镜像运行API，避免把构建依赖与私密资料带入最终镜像。

### 输入、输出与调用关系

仓库构建上下文→前端JS→非root运行的8000端口API镜像。

### 运行与风险边界

需要Docker环境才运行 `docker build -f deploy/Dockerfile -t evidencedesk .`；本轮未构建。启用演示需显式EVIDENCEDESK_DEMO=1。

拉镜像/安装依赖需要网络与资源；基础tag未固定digest，非完全字节复现。镜像不自动创建数据库或连接模型。

## 完整源码

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

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```dockerfile
#: 前端构建阶段只用于编译；最终镜像不携带 node_modules。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：前端构建阶段只用于编译；最终镜像不携带 node_modules。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```dockerfile
FROM node:22-bookworm-slim AS frontend
```

**语法与数据变化：** 以Node22 Debian slim为构建阶段，别名frontend。

**为什么与边界：** AS供后面COPY引用；此阶段不是最终服务器镜像。

<a id="L3"></a>
### 第 3 行

```dockerfile
WORKDIR /web
```

**语法与数据变化：** 设置工作目录/web，后续相对路径基于它。

**为什么与边界：** 目录在镜像中，不是修改宿主机cwd。

<a id="L4"></a>
### 第 4 行

```dockerfile
COPY frontend/package*.json ./
```

**语法与数据变化：** 先复制package.json和lock以利依赖层缓存。

**为什么与边界：** 构建上下文必须是仓库根目录。

<a id="L5"></a>
### 第 5 行

```dockerfile
RUN npm ci --ignore-scripts
```

**语法与数据变化：** npm ci严格使用锁文件，ignore-scripts禁依赖生命周期脚本。

**为什么与边界：** 仍联网取包；禁脚本不等于第三方依赖已安全审计。

<a id="L6"></a>
### 第 6 行

```dockerfile
COPY frontend/ ./
```

**语法与数据变化：** 复制前端源码和配置。

**为什么与边界：** .dockerignore防止本机node_modules进入上下文。

<a id="L7"></a>
### 第 7 行

```dockerfile
RUN npm run build
```

**语法与数据变化：** 执行项目build脚本即tsc。

**为什么与边界：** 有类型错误应失败，不把坏JS带入最终阶段。

<a id="L8"></a>
### 第 8 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L9"></a>
### 第 9 行

```dockerfile
#: 复制明确的课程运行文件，不把 .env、Git 或原始数据打包进去。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：复制明确的课程运行文件，不把 .env、Git 或原始数据打包进去。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L10"></a>
### 第 10 行

```dockerfile
FROM python:3.11-slim
```

**语法与数据变化：** 开始独立Python3.11最终阶段。

**为什么与边界：** 前阶段Node环境不会自动继承。

<a id="L11"></a>
### 第 11 行

```dockerfile
WORKDIR /app
```

**语法与数据变化：** 设置运行目录/app。

**为什么与边界：** API相对语料/静态路径据此定位。

<a id="L12"></a>
### 第 12 行

```dockerfile
COPY pyproject.toml requirements-tested.lock.txt ./
```

**语法与数据变化：** 复制Python项目配置与已测依赖快照。

**为什么与边界：** 快照不是所有未来环境永久可装的保证。

<a id="L13"></a>
### 第 13 行

```dockerfile
COPY src/ ./src/
```

**语法与数据变化：** 只复制应用src。

**为什么与边界：** 不把课程草稿、Git或用户笔记整体COPY进镜像。

<a id="L14"></a>
### 第 14 行

```dockerfile
COPY data/sample/ ./data/sample/
```

**语法与数据变化：** 只带公开虚构样例。

**为什么与边界：** 没有默认上传下载语料或真实客户数据。

<a id="L15"></a>
### 第 15 行

```dockerfile
COPY --from=frontend /web/index.html /web/client.js ./frontend/
```

**语法与数据变化：** 从frontend阶段取HTML和编译JS到运行目录。

**为什么与边界：** 不带TS编译器和node_modules，缩小最终镜像。

<a id="L16"></a>
### 第 16 行

```dockerfile
RUN pip install --no-cache-dir -r requirements-tested.lock.txt && pip install --no-deps -e .
```

**语法与数据变化：** 安装快照后以--no-deps可编辑安装本包，&&要求前者成功。

**为什么与边界：** --no-cache-dir减少pip缓存，不等于不用网络；可编辑布局需src留在镜像内。

<a id="L17"></a>
### 第 17 行

```dockerfile
#: 非 root 运行；对外绑定 0.0.0.0，浏览器请求仍使用同源相对路径。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：非 root 运行；对外绑定 0.0.0.0，浏览器请求仍使用同源相对路径。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L18"></a>
### 第 18 行

```dockerfile
RUN useradd --create-home appuser
```

**语法与数据变化：** 创建带home的非root用户。

**为什么与边界：** 原部署未固定UID，Space导出器另改1000以适配平台。

<a id="L19"></a>
### 第 19 行

```dockerfile
USER appuser
```

**语法与数据变化：** 后续运行命令使用appuser。

**为什么与边界：** 非root减小权限，不是完整容器安全隔离策略。

<a id="L20"></a>
### 第 20 行

```dockerfile
EXPOSE 8000
```

**语法与数据变化：** 声明8000服务端口元信息。

**为什么与边界：** EXPOSE不自动将宿主/公网端口发布，需要运行平台配置。

<a id="L21"></a>
### 第 21 行

```dockerfile
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"
```

**语法与数据变化：** 容器内部Python请求127.0.0.1健康接口，超时3秒。

**为什么与边界：** 此localhost在容器内合理，浏览器代码不得拿它指向沙箱后端；只测健康路由。

<a id="L22"></a>
### 第 22 行

```dockerfile
CMD ["uvicorn", "evidencedesk.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**语法与数据变化：** exec形式CMD启动uvicorn app，绑定0.0.0.0:8000。

**为什么与边界：** 可接受平台代理连接，未在此行启用演示模式；需外部环境变量显式配置。

## 跟一遍数据与验证边界

最终镜像COPY固定src/sample/frontend，不带node_modules；健康200仍不保证演示模式已开或模型/数据库可用。

## 只练一个关键点（不是新的学习验收记录）

1. 先标出两段FROM和跨阶段COPY，不直接声称镜像已构建。
2. 有Docker且本课同意后再构建；确认只带虚构语料，启用演示时显式设置环境。
3. **复盘：** EXPOSE、0.0.0.0监听、平台端口发布分别做什么？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
