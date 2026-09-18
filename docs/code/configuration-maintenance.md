# 补充配置、依赖锁与维护规则

[源码精讲目录](index.md) · [覆盖口径](../course/code-explanation-coverage.md)

这些10份文件单列为**配置字段/规则与维护讲解**，不混入51份主清单逐行源码覆盖率。忽略规则、小配置逐项说明；锁文件讲结构、真实用途和更新流程，不把每条第三方依赖记录伪装成业务实现。完整原文仍可对照，并纳入摘要/副本同步检查。

<a id="config-1"></a>
## 1. `.dockerignore`：Docker构建上下文的排除规则

[实际文件](../../.dockerignore)

Docker发送构建上下文之前读取此文件，不等于Git忽略规则。即使Dockerfile只COPY白名单，也不要把秘密作为构建上下文发送。

| 行 | 具体作用与边界 |
|---|---|
| 1 | `.git`排除版本历史与元数据；镜像不需要提交记录。 |
| 2 | `.venv`排除本机解释器环境；依赖应在镜像中按配置重装。 |
| 3 | `**/__pycache__`排除任意深度Python字节码缓存，不删除源码。 |
| 4 | `**/node_modules`排除本机Node依赖，构建阶段用npm ci重新安装。 |
| 5 | `.env`排除本地环境变量文件；不能因此把Key写在其他文件里。 |
| 6 | `.env.*`也排除带后缀的环境文件，此处没有像Git规则那样放行example。 |
| 7 | `data/raw`排除下载原件与潜在用户输入。 |
| 8 | `data/processed`排除派生语料，不等于它已获授权上传。 |
| 9 | `artifacts`排除生成ZIP、数据库和实验报告。 |

**练习：** 对照Dockerfile的COPY和Space导出白名单，分别指出“不会发送上下文”和“不会复制进最终镜像”的保护层。不要为试验故意放入真实密钥。

### 完整配置原文

<!-- source: .dockerignore -->
```text
.git
.venv
**/__pycache__
**/node_modules
.env
.env.*
data/raw
data/processed
artifacts
```

<a id="config-2"></a>
## 2. `.gitignore`：Git忽略规则与生成物边界

[实际文件](../../.gitignore)

忽略规则影响尚未跟踪文件的默认发现/添加，不会自动清除已经提交的秘密。泄漏过的Key应撤销/轮换，不能只加一条ignore。

| 行 | 含义与理由 |
|---|---|
| 1、14、19、27、32 | `#`开头是分类注释，不是模式；空行13、18、26、31用于分隔。 |
| 2 | `.venv/`不提交机器相关的虚拟环境。 |
| 3 | `__pycache__/`不提交Python缓存目录。 |
| 4 | `*.py[cod]`中的方括号匹配c/o/d任一后缀，排除编译缓存等产物。 |
| 5 | `.pytest_cache/`是测试缓存，不是测试源码。 |
| 6 | `.ruff_cache/`是代码检查缓存。 |
| 7 | `.mypy_cache/`是静态类型检查缓存。 |
| 8 | `*.egg-info/`是安装/构建元数据，不当成手写实现。 |
| 9 | `build/`排除构建中间目录。 |
| 10 | `dist/`排除分发产物目录。 |
| 11 | `.coverage`排除覆盖率原始数据。 |
| 12 | `htmlcov/`排除覆盖率HTML报告；测试源码仍要跟踪。 |
| 15 | `.env`默认不提交环境配置与秘密。 |
| 16 | `.env.*`扩展到带环境后缀的文件。 |
| 17 | `!`反向规则重新允许`.env.example`；示例只能放名称/假值，不能放真Key。 |
| 20 | `data/raw/`外部原始输入不进源码库。 |
| 21 | `data/processed/`处理后副本可重建，仍可能含敏感内容。 |
| 22 | `data/indexes/`排除生成索引，不应把模型向量误当业务源码。 |
| 23 | `artifacts/`排除PDF、数据库、导出ZIP等产物。 |
| 24 | `runs/`排除实验运行数据。 |
| 25 | `logs/`排除日志；忽略不等于脱敏或安全删除。 |
| 28 | `node_modules/`依赖由npm锁文件恢复，不提交第三方安装树。 |
| 29 | `.next/`是框架构建缓存，当前简易前端不依赖它。 |
| 30 | `.DS_Store`是系统目录元数据。 |
| 33 | `frontend/client.js`由client.ts编译生成，提交TS和配置即可。 |

**练习：** 运行 `git check-ignore -v frontend/client.js artifacts/demo.pdf`，看是哪条规则命中；不要运行`git add -f`强行加入产物。用户自己的未跟踪笔记不是本轮自动添加对象。

### 完整配置原文

<!-- source: .gitignore -->
```text
# Python and local environments
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.mypy_cache/
*.egg-info/
build/
dist/
.coverage
htmlcov/

# Secrets and local config
.env
.env.*
!.env.example

# Generated data / indexes / runs (keep curated fixtures tracked)
data/raw/
data/processed/
data/indexes/
artifacts/
runs/
logs/

# Frontend / editors
node_modules/
.next/
.DS_Store

# Reproducible frontend output and generated course experiment results
frontend/client.js
```

<a id="config-3"></a>
## 3. `data/sources/fastapi.json`：公开语料来源清单

[实际文件](../../data/sources/fastapi.json)

这是下载器的受控输入，不是业务题集或数据库连接配置。

- L1/L12外层对象，L7/L11文档数组：花括号与方括号不能互换；JSON不支持注释或随意末尾逗号。
- L2 `repository`指定GitHub仓库；L3 `revision`固定commit。改成main会使重跑输入漂移。
- L4 `license`记录预期MIT，L5 `license_path`定位原许可文件；声明不代替实际下载、保留和复核许可。
- L6 `purpose`提醒这是英语真实公开开发者资料，不与虚构Northstar的gold标签混用。
- L8 第一份部署概念、L9 第二份HTTPS、L10 第三份安全入门，各有`id`（输出文件/文档身份）、`title`（规范文档首标题）、`path`（固定revision内的源路径）。ID必须受控，当前下载器不是任意不可信清单的路径沙箱。

**维护步骤：** 先审查新路径/许可证与体量→明确更新revision→重新下载到ignored目录→比较raw hash与来源报告→为新语料单独构建题集。改清单并不自动更新API或向量索引。

**练习：** 只选一条记录，用文字说明它如何经`github_file`变成raw、processed与provenance三类产物；此阅读不要求重新联网下载。

### 完整配置原文

<!-- source: data/sources/fastapi.json -->
```json
{
  "repository": "fastapi/fastapi",
  "revision": "50113da16fec53b66b80d75e80a89296de4fa5a5",
  "license": "MIT",
  "license_path": "LICENSE",
  "purpose": "公开的开发者支持资料；独立于虚构 Northstar Cloud 手册，不混用两套评测标签。",
  "documents": [
    {"id": "fastapi-deployment-concepts", "title": "FastAPI Deployment Concepts", "path": "docs/en/docs/deployment/concepts.md"},
    {"id": "fastapi-https", "title": "FastAPI About HTTPS", "path": "docs/en/docs/deployment/https.md"},
    {"id": "fastapi-security-first-steps", "title": "FastAPI Security First Steps", "path": "docs/en/docs/tutorial/security/first-steps.md"}
  ]
}
```

<a id="config-4"></a>
## 4. `frontend/package.json`：前端命令与直接开发依赖

[实际文件](../../frontend/package.json)

文件只有一个物理行，但含多个字段，不能只说“这是npm配置”。

- `name`是本地包身份，`version`是课程UI版本，不是缓存查询串。
- `private: true`防止误用npm publish发布包，不是访问控制或内容加密。
- `scripts.build: "tsc"`让`npm run build`调用本项目安装的TypeScript编译器，不启动开发服务器。
- `devDependencies.typescript: "5.9.3"`固定直接编译依赖；它不进入浏览器运行时。精确版本与package-lock共同维护。

**练习：** 先`npm --prefix frontend ci --ignore-scripts`，再`npm --prefix frontend run build`；确认生成client.js而不是新增常驻服务器。更新TS时同时审查锁文件并重新编译/检查浏览器，不手改版本后就宣称兼容。

### 完整配置原文

<!-- source: frontend/package.json -->
```json
{"name":"evidencedesk-course-ui","private":true,"version":"0.1.0","scripts":{"build":"tsc"},"devDependencies":{"typescript":"5.9.3"}}
```

<a id="config-5"></a>
## 5. `frontend/tsconfig.json`：TypeScript编译和错误门禁

[实际文件](../../frontend/tsconfig.json)

同样是一行JSON，必须按字段理解：

- `compilerOptions.target=ES2022`选择输出JavaScript语言能力，须考虑目标浏览器。
- `module=ES2022`保持ES模块输出，与HTML的`type=module`一致。
- `lib=[ES2022,DOM]`给标准语言和浏览器DOM提供类型声明，不是给浏览器安装polyfill。
- `strict=true`启用严格检查；但源码中的非空断言`!`仍可能掩盖运行时缺节点。
- `noEmitOnError=true`有编译错误时不发出新输出；它不保证删除上次成功留下的旧client.js，失败后不可部署陈旧产物。
- `files=[client.ts]`显式指定入口文件；新增TS入口需要复核收集范围。

**练习：** 在副本中把一个`Hit.score`使用位置赋成不兼容类型，运行构建观察错误，然后恢复并重新构建。不要用关闭strict来消除真正的类型问题。

### 完整配置原文

<!-- source: frontend/tsconfig.json -->
```json
{"compilerOptions":{"target":"ES2022","module":"ES2022","lib":["ES2022","DOM"],"strict":true,"noEmitOnError":true},"files":["client.ts"]}
```

<a id="config-6"></a>
## 6. `requirements-database.txt`：数据库客户端的独立依赖层

[实际文件](../../requirements-database.txt)

L1注释说明这是可选本地PG客户端，服务器二进制另外由npm管理。L2固定`psycopg==3.3.5`Python接口，L3固定配套`psycopg-binary==3.3.5`二进制组件；`==`是精确版本，而非`>=`范围。

**维护：** 两者配套升级，核对Python/平台支持及安全公告，再在自有本地实验跑RLS。安装它们不会自动运行PostgreSQL、创建云库或让SQLite代码改用PG。

**练习：** 区分`pip show psycopg`看到的客户端版本与`tools.local_postgres version`打印的服务器版本。只有确实准备数据库课时才安装：`python -m pip install -r requirements-database.txt`。

### 完整配置原文

<!-- source: requirements-database.txt -->
```text
# Optional local PostgreSQL lab client; runtime binaries are pinned via npm separately.
psycopg==3.3.5
psycopg-binary==3.3.5
```

<a id="config-7"></a>
## 7. `requirements-tested.lock.txt`：已测Python环境快照：不是第三方源码教材

[实际文件](../../requirements-tested.lock.txt)

L1限定历史验收环境为Python3.11/Linux，并明确可选付费模型实验未验收。其余每行统一使用`分发包名==精确版本`语法；包名不一定等于Python import名，例如PyYAML常导入yaml。

**按角色读，而不是背77行：** pytest/pluggy等支撑测试；FastAPI/Starlette/Pydantic/Uvicorn支撑API；httpx及底层传输包支撑请求；qdrant-client/numpy支撑向量实验；pypdf/tiktoken支撑文本提取与计数；LangGraph/MCP及各协议组件支撑流程/工具；LangChain/OpenAI/LangSmith是可选模型/追踪接口。证书、加密、类型与压缩库多是传递依赖，仍需安全更新，不能因不是手写源码就忽略漏洞。

**边界：** 这是pip风格快照，不含轮子hash，也不保证所有操作系统未来永久可装。文件里有openai并不代表发生过真实模型调用；有langsmith不代表已上传遥测。Ragas、SentenceTransformers、DeepAgents等可选示例依赖并未由这份快照完整包办，按对应课程另行核对。

**更新步骤：** 在干净隔离环境安装目标范围→记录Python/OS及直接依赖选择→跑无密钥测试、前端和课程检查→审查`pip freeze`与`pip check`→只提交有证据的新快照及验证记录。不能直接把个人全局环境所有包冻结进去，也不能为本轮文档补写无故升级整个依赖栈。

**本轮验证的区别：** 本轮使用项目extras重新建立离线测试环境并通过63项测试，未重新证明此历史快照逐版本安装成功。不要把两个环境写成完全相同。

**练习：** 选pytest、httpx、pypdf三个包，在快照找精确版本并对照pyproject允许范围；再看当前`python -m pip show`，记录差异而不是覆盖快照。

### 完整配置原文

<!-- source: requirements-tested.lock.txt -->
```text
# Python 3.11/Linux tested snapshot; optional paid-model labs are not acceptance-tested.
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.15.1
attrs==26.1.0
certifi==2026.7.22
cffi==2.1.1
charset-normalizer==3.5.1
click==8.5.0
cryptography==50.0.1
distro==1.9.0
fastapi==0.141.1
grpcio==1.83.1
h11==0.16.0
h2==4.4.1
hpack==4.2.0
httpcore==1.0.9
httpcore2==2.12.0
httpx==0.28.1
httpx-sse==0.4.3
httpx2==2.12.0
hyperframe==6.1.0
idna==3.19
iniconfig==2.3.0
jiter==0.17.0
jsonpatch==1.33
jsonpointer==3.1.1
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
langchain-core==1.6.3
langchain-openai==1.6.2
langchain-protocol==0.0.19
langgraph==1.2.11
langgraph-checkpoint==4.2.0
langgraph-prebuilt==1.1.0
langgraph-sdk==0.4.4
langsmith==0.12.4
mcp==1.30.0
numpy==2.4.6
openai==3.13.0
orjson==3.12.0
ormsgpack==1.12.2
packaging==26.3
pluggy==1.6.0
portalocker==3.2.0
protobuf==7.36.1
pycparser==3.0
pydantic==2.13.5
pydantic-settings==2.15.0
pydantic_core==2.46.5
Pygments==2.21.0
PyJWT==2.14.0
pypdf==6.18.1
pytest==8.4.2
python-dotenv==1.2.3
python-multipart==0.0.32
PyYAML==6.0.3
qdrant-client==1.19.0
referencing==0.37.0
regex==2026.9.10
requests==2.34.2
requests-toolbelt==1.0.0
rpds-py==2026.6.3
sniffio==1.3.1
sse-starlette==3.4.11
starlette==1.6.0
tenacity==9.1.4
tiktoken==0.14.0
truststore==0.10.4
typing-inspection==0.4.4
typing_extensions==4.16.0
urllib3==2.7.0
uuid_utils==0.17.1
uvicorn==0.52.4
websockets==16.1.1
xxhash==4.0.1
zstandard==0.25.0
```

<a id="config-8"></a>
## 8. `frontend/package-lock.json`：前端npm锁文件的结构与更新

[实际文件](../../frontend/package-lock.json)

npm生成文件，不手改某个integrity来让安装通过。

- 顶层`name/version`对应包身份；`lockfileVersion:3`是npm锁格式，不是TypeScript版本；`requires`是锁格式元数据。
- `packages[""]`记录根项目及直接devDependencies；`packages["node_modules/typescript"]`记录实际解析包。
- 包的`version`固定5.9.3，`resolved`是来源归档URL，`integrity`用于校验下载内容。完整性匹配不等于供应链完全无恶意。
- `dev:true`标明开发依赖，`license`记录包许可信息，仍应核对所用版本的许可文件。
- `bin.tsc`与`bin.tsserver`是命令到包内文件的映射；前者编译，后者服务编辑器，不需常驻启动后者。
- `engines.node`说明最低Node要求；部署选择Node22并非这份锁主动安装了Node。
- 花括号/逗号只是JSON结构边界，不是可执行业务语句。

**维护：** 日常用`npm ci --ignore-scripts`严格按锁恢复；需要升级时显式更新package.json并由npm重新解析锁，然后审diff、编译和测试。不要靠删除锁文件让不可复现安装“碰巧成功”。

**练习：** 对照package.json的typescript版本与锁的根依赖/实际包版本三处一致性；无需逐行学习TypeScript编译器的第三方实现。

### 完整配置原文

<!-- source: frontend/package-lock.json -->
```json
{
  "name": "evidencedesk-course-ui",
  "version": "0.1.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "evidencedesk-course-ui",
      "version": "0.1.0",
      "devDependencies": {
        "typescript": "5.9.3"
      }
    },
    "node_modules/typescript": {
      "version": "5.9.3",
      "resolved": "https://registry.npmjs.org/typescript/-/typescript-5.9.3.tgz",
      "integrity": "sha512-jl1vZzPDinLr9eUt3J/t7V6FgNEw9QjvBPdysz9KfQDD41fQrC2Y4vKQdiaUpFT4bXlb1RHhLpp8wtm6M5TgSw==",
      "dev": true,
      "license": "Apache-2.0",
      "bin": {
        "tsc": "bin/tsc",
        "tsserver": "bin/tsserver"
      },
      "engines": {
        "node": ">=14.17"
      }
    }
  }
}
```

<a id="config-9"></a>
## 9. `tools/postgres-runtime/package.json`：本地数据库实验的二进制分发依赖

[实际文件](../../tools/postgres-runtime/package.json)

这一行JSON的`name/version`标记独立实验包，`private:true`避免误publish；`description`限定第三方二进制、Linux x64、仅沙箱实验。`dependencies`把`@embedded-postgres/linux-x64`固定在18.4.0-beta.17。

**边界：** npm分发版本字符串与真实PostgreSQL服务器版本是两类标识。不要据此推荐生产数据库安全部署；本机二进制需要平台与动态库匹配。

**维护/练习：** 先核对CPU/OS及包来源、锁文件，再按数据库课用`npm --prefix tools/postgres-runtime ci --ignore-scripts`安装。生命周期脚本被禁用后，由受限的local_postgres.runtime准备必要链接；不是直接运行陌生安装脚本。

### 完整配置原文

<!-- source: tools/postgres-runtime/package.json -->
```json
{"name":"evidencedesk-postgres-lab-runtime","private":true,"version":"0.1.0","description":"Pinned third-party PostgreSQL binaries for the Linux x64 sandbox lab only","dependencies":{"@embedded-postgres/linux-x64":"18.4.0-beta.17"}}
```

<a id="config-10"></a>
## 10. `tools/postgres-runtime/package-lock.json`：数据库二进制锁、平台与安装脚本风险

[实际文件](../../tools/postgres-runtime/package-lock.json)

与前端锁共享name/version/lockfileVersion/packages/version/resolved/integrity语义，但还有特别重要的字段：

- 根`dependencies`与实际包版本应一致，不能只改其中一个。
- `cpu:[x64]`与`os:[linux]`限制目标平台，macOS/ARM不能把该包当通用服务器。
- `hasInstallScript:true`提示包含安装脚本。教学安装显式`--ignore-scripts`，并不表示包没有脚本；必要符号链接由项目受控代码处理。
- `license:MIT`是这个npm分发包记录的许可，不应据此忽略内含数据库/动态库各自许可与安全公告。
- `engines.node:>=16`约束npm运行环境，不决定PostgreSQL协议版本。
- `resolved`/`integrity`约束取得的归档；哈希正确不意味着老动态库没有已知安全问题。

**维护/练习：** 只阅读这些元数据并对照local_postgres路径检查；若将来更新包，重新核验平台、原生依赖、链接清单、真实版本和RLS/重启实验。不能把`npm audit 0`当成整个数据库及捆绑原生库无漏洞证明。

### 完整配置原文

<!-- source: tools/postgres-runtime/package-lock.json -->
```json
{
  "name": "evidencedesk-postgres-lab-runtime",
  "version": "0.1.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "evidencedesk-postgres-lab-runtime",
      "version": "0.1.0",
      "dependencies": {
        "@embedded-postgres/linux-x64": "18.4.0-beta.17"
      }
    },
    "node_modules/@embedded-postgres/linux-x64": {
      "version": "18.4.0-beta.17",
      "resolved": "https://registry.npmjs.org/@embedded-postgres/linux-x64/-/linux-x64-18.4.0-beta.17.tgz",
      "integrity": "sha512-jVw/MdDtIX/vICH/DKIe6/mHpiCggdx6QVyza4vt/NbcZFsL0KhwglF6F1Koqx3gRBZ9XtN+vi63EsqSyqOSxA==",
      "cpu": [
        "x64"
      ],
      "hasInstallScript": true,
      "license": "MIT",
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">=16"
      }
    }
  }
}
```
