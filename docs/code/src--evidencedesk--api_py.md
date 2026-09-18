# FastAPI 演示接口与授权过滤：逐行精讲

[精讲总目录](index.md) · [对应源码](../../src/evidencedesk/api.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

给虚构手册提供同源HTTP检索接口，并把身份、输入验证、可见文档过滤与输出分开。

### 输入、输出与调用关系

浏览器POST JSON，经Query验证和identity依赖得到tenant；输出命中列表或SSE帧。静态前端由同一应用挂载。

### 运行与风险边界

按零预算指南启动演示服务；必须显式设置 EVIDENCEDESK_DEMO=1，并绑定0.0.0.0供预览访问。测试可用 `python -m pytest tests/test_api.py -q`。

公开固定token只适用虚构资料；不是生产认证。未接入PostgreSQL或模型。X-Demo-Token用于避免预览代理可能占用Authorization，不宣称已直接观测代理根因。

## 完整源码

<!-- source: src/evidencedesk/api.py -->
```python
#: 真实 FastAPI 接口，但只服务虚构手册；固定演示令牌不是生产身份体系。
import json
import os
from dataclasses import asdict
from pathlib import Path
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .documents import load_documents
from .search import search

#: 此源码布局依赖 editable install 和仓库目录；不能把单独 wheel 当完整部署包。
ROOT = Path(__file__).resolve().parents[2]
app = FastAPI(title="EvidenceDesk · 候选证据演示")
DEMO_IDENTITIES = {"demo-alice": "alpha", "demo-bob": "beta"}
ACL = {"alpha": {"webhook-delivery", "api-key-policy"}, "beta": {"incident-escalation"}}

#: 演示专用头避开预览代理可能占用的 Authorization；仅显式启用虚构演示时生效。
def identity(authorization: str = Header(default=""),
             demo_token: str | None = Header(default=None, alias="X-Demo-Token")) -> str:
    if os.environ.get("EVIDENCEDESK_DEMO") != "1":
        raise HTTPException(503, "虚构数据演示需设置 EVIDENCEDESK_DEMO=1；不是生产鉴权")
    #: 专用头存在时只校验该值，不因它无效就回退；Bearer 保留给旧 CLI 示例。
    token = demo_token if demo_token is not None else (authorization[7:] if authorization.startswith("Bearer ") else None)
    tenant = DEMO_IDENTITIES.get(token)
    if tenant is None:
        raise HTTPException(401, "缺少或无效的演示身份；刷新页面并重新选择用户，无需 Agnes API Key")
    return tenant

#: 限制输入长度和 k；strict 防止 True 或字符串被自动转换成整数。
class Query(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    k: int = Field(default=3, ge=1, le=10, strict=True)

@app.get("/health")
def health():
    return {"status": "ok", "mode": "offline-evidence-demo"}

#: 先按服务端身份筛可见文档再检索；不能搜完整库后让模型决定权限。
@app.post("/api/search")
def retrieve(query: Query, tenant: str = Depends(identity)):
    visible = [doc for doc in load_documents(ROOT / "data/sample") if doc.id in ACL[tenant]]
    return [asdict(hit) for hit in search(query.question, visible, query.k)]

#: 演示 SSE 帧格式，不是 LLM token 流；先完成检索再发 evidence 和 done 两个事件。
@app.post("/api/events")
def events(query: Query, tenant: str = Depends(identity)):
    hits = retrieve(query, tenant)
    def stream():
        yield "event: evidence\ndata: " + json.dumps(hits, ensure_ascii=False) + "\n\n"
        yield 'event: done\ndata: {}\n\n'
    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

#: 静态挂载在 API 路由之后；前端 fetch 相对路径，同源无需宽泛开放 CORS。
app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: 真实 FastAPI 接口，但只服务虚构手册；固定演示令牌不是生产身份体系。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：真实 FastAPI 接口，但只服务虚构手册；固定演示令牌不是生产身份体系。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
import json
```

**语法与数据变化：** 导入 `json` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 JSON 编解码器。loads/读入负责解析，dumps 负责生成字符串；JSON 的 true/null 与 Python 的 True/None 对应，序列化不验证事实。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
import os
```

**语法与数据变化：** 导入 `os` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库操作系统接口，用于环境变量、目录权限或进程环境。环境变量来自进程，不会因为代码中有名字就自动配置。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

```python
from dataclasses import asdict
```

**语法与数据变化：** 从 `dataclasses` 导入 `asdict`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 数据类工具。dataclass 自动生成初始化及比较等方法，asdict 转字典，field 控制字段默认值；普通字段类型注解不自动验证输入。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
from pathlib import Path
```

**语法与数据变化：** 从 `pathlib` 导入 `Path`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 标准库的路径对象。Path 的 / 表示拼接路径；构造对象不读文件，read_text/exists 等方法才执行相应操作。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

```python
from fastapi import Depends, FastAPI, Header, HTTPException
```

**语法与数据变化：** 从 `fastapi` 导入 `Depends, FastAPI, Header, HTTPException`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Web 框架。路由、依赖与 Header/HTTPException 共同定义 HTTP 契约；演示身份不等于生产认证。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L7"></a>
### 第 7 行

```python
from fastapi.responses import StreamingResponse
```

**语法与数据变化：** 从 `fastapi.responses` 导入 `StreamingResponse`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 响应类型。StreamingResponse 消费迭代器输出流；有流式格式不代表后端正在逐 token 生成。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L8"></a>
### 第 8 行

```python
from fastapi.staticfiles import StaticFiles
```

**语法与数据变化：** 从 `fastapi.staticfiles` 导入 `StaticFiles`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 静态文件服务。把目录映射到 URL；挂载范围和路由顺序影响可见文件，不能任意暴露仓库根目录。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L9"></a>
### 第 9 行

```python
from pydantic import BaseModel, Field
```

**语法与数据变化：** 从 `pydantic` 导入 `BaseModel, Field`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 运行时数据模型和字段约束。它与普通 Python 类型注解不同；校验 JSON 结构和字段类型不保证内容事实正确。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L10"></a>
### 第 10 行

```python
from .documents import load_documents
```

**语法与数据变化：** 从 `.documents` 导入 `load_documents`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** Document承载id/title/text/source四字段；load_documents把合规Markdown目录转换为对象列表，并明确区分空目录与读取/格式错误。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L11"></a>
### 第 11 行

```python
from .search import search
```

**语法与数据变化：** 从 `.search` 导入 `search`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** search用固定领域词覆盖率返回排序的SearchHit候选；不是模型生成或语义检索。权限过滤应在调用之前完成。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L12"></a>
### 第 12 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L13"></a>
### 第 13 行

```python
#: 此源码布局依赖 editable install 和仓库目录；不能把单独 wheel 当完整部署包。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：此源码布局依赖 editable install 和仓库目录；不能把单独 wheel 当完整部署包。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L14"></a>
### 第 14 行

```python
ROOT = Path(__file__).resolve().parents[2]
```

**语法与数据变化：** parents[2]取第三个父目录：api.py→evidencedesk→src→仓库。

**为什么与边界：** 依赖源码布局；打包成不带data/frontend的单独wheel后，这种定位不能保证资源存在。

<a id="L15"></a>
### 第 15 行

```python
app = FastAPI(title="EvidenceDesk · 候选证据演示")
```

**语法与数据变化：** 创建FastAPI应用对象并设置展示标题。

**为什么与边界：** 创建对象不等于启动HTTP服务器，仍需uvicorn等ASGI服务运行。

<a id="L16"></a>
### 第 16 行

```python
DEMO_IDENTITIES = {"demo-alice": "alpha", "demo-bob": "beta"}
```

**语法与数据变化：** 固定token映射到租户alpha/beta。

**为什么与边界：** 这些是公开演示身份，不是私密用户凭证；绝不能给真实资料复用此认证方式。

<a id="L17"></a>
### 第 17 行

```python
ACL = {"alpha": {"webhook-delivery", "api-key-policy"}, "beta": {"incident-escalation"}}
```

**语法与数据变化：** ACL定义每租户可见的文档ID集合。

**为什么与边界：** 权限存在服务端，而不是由浏览器或LLM决定；集合必须与语料ID保持一致。

<a id="L18"></a>
### 第 18 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L19"></a>
### 第 19 行

```python
#: 演示专用头避开预览代理可能占用的 Authorization；仅显式启用虚构演示时生效。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：演示专用头避开预览代理可能占用的 Authorization；仅显式启用虚构演示时生效。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L20"></a>
### 第 20 行

```python
def identity(authorization: str = Header(default=""),
```

**语法与数据变化：** identity是依赖函数，第一个参数通过Header读取Authorization，缺失给空串。

**为什么与边界：** 直接调用函数与FastAPI注入不同；不要把Header对象默认值当成测试时自动请求头。

<a id="L21"></a>
### 第 21 行

```python
             demo_token: str | None = Header(default=None, alias="X-Demo-Token")) -> str:
```

**语法与数据变化：** 第二个参数读取显式别名X-Demo-Token，缺失用None以区分“没传”和“传空值”。

**为什么与边界：** 专用头是适配演示代理的选择，不增加真实用户认证强度。

<a id="L22"></a>
### 第 22 行

```python
    if os.environ.get("EVIDENCEDESK_DEMO") != "1":
```

**语法与数据变化：** 读取进程环境，只有精确字符串"1"才允许演示身份。

**为什么与边界：** 布尔True或其他字符串不会自动等价，默认拒绝可以减少误开放风险。

<a id="L23"></a>
### 第 23 行

```python
        raise HTTPException(503, "虚构数据演示需设置 EVIDENCEDESK_DEMO=1；不是生产鉴权")
```

**语法与数据变化：** 演示未启用返回503，并明确这不是生产鉴权。

**为什么与边界：** 503是服务模式不可用，不是搜索不到证据。

<a id="L24"></a>
### 第 24 行

```python
    #: 专用头存在时只校验该值，不因它无效就回退；Bearer 保留给旧 CLI 示例。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：专用头存在时只校验该值，不因它无效就回退；Bearer 保留给旧 CLI 示例。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L25"></a>
### 第 25 行

```python
    token = demo_token if demo_token is not None else (authorization[7:] if authorization.startswith("Bearer ") else None)
```

**语法与数据变化：** 专用头只要存在就采用它；否则仅在Bearer前缀正确时取后面的token。

**为什么与边界：** 专用头无效不能回退到另一个有效头，否则会形成混淆身份的绕过路径。

<a id="L26"></a>
### 第 26 行

```python
    tenant = DEMO_IDENTITIES.get(token)
```

**语法与数据变化：** 用映射查租户，不存在返回None。

**为什么与边界：** 没有数据库或模型参与身份解析，也不要信任用户提交的tenant参数。

<a id="L27"></a>
### 第 27 行

```python
    if tenant is None:
```

**语法与数据变化：** 未命中演示身份表即拒绝。

**为什么与边界：** 空串、未知token等都会走这里。

<a id="L28"></a>
### 第 28 行

```python
        raise HTTPException(401, "缺少或无效的演示身份；刷新页面并重新选择用户，无需 Agnes API Key")
```

**语法与数据变化：** 抛HTTPException(401)，给出可操作的演示身份错误说明。

**为什么与边界：** 不要把401转成200 []；否则用户会把授权问题误认为检索质量问题。

<a id="L29"></a>
### 第 29 行

```python
    return tenant
```

**语法与数据变化：** 返回已确认的服务端tenant字符串。

**为什么与边界：** 后面的依赖注入据此筛资料，不能在模型输出后才决定权限。

<a id="L30"></a>
### 第 30 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L31"></a>
### 第 31 行

```python
#: 限制输入长度和 k；strict 防止 True 或字符串被自动转换成整数。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：限制输入长度和 k；strict 防止 True 或字符串被自动转换成整数。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L32"></a>
### 第 32 行

```python
class Query(BaseModel):
```

**语法与数据变化：** Query继承Pydantic BaseModel，使FastAPI对请求JSON做运行时验证。

**为什么与边界：** 这比普通函数注解更强，但不是事实审核或权限控制。

<a id="L33"></a>
### 第 33 行

```python
    question: str = Field(min_length=1, max_length=1000)
```

**语法与数据变化：** question要求长度1–1000的字符串字段。

**为什么与边界：** 本行没有strip，纯空格长度仍可能合格，后面的词检索可返回空；若需拒绝空白要另写规则。

<a id="L34"></a>
### 第 34 行

```python
    k: int = Field(default=3, ge=1, le=10, strict=True)
```

**语法与数据变化：** k缺省3、范围1–10且strict=True。

**为什么与边界：** strict阻止True或"3"被自动接受为整数，与argparse处理终端字符串的设计不同。

<a id="L35"></a>
### 第 35 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L36"></a>
### 第 36 行

```python
@app.get("/health")
```

**语法与数据变化：** 装饰器注册GET /health到下面函数。

**为什么与边界：** 注册路由不是执行一次健康检查，也不检查外部模型/数据库是否可用。

<a id="L37"></a>
### 第 37 行

```python
def health():
```

**语法与数据变化：** 定义无参健康处理器。

**为什么与边界：** 函数只返回当前离线模式描述，不做依赖探活。

<a id="L38"></a>
### 第 38 行

```python
    return {"status": "ok", "mode": "offline-evidence-demo"}
```

**语法与数据变化：** 返回字典，FastAPI将它编码为JSON。

**为什么与边界：** status=ok只覆盖这个轻量入口，不代表全部检索/鉴权/部署都正确。

<a id="L39"></a>
### 第 39 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L40"></a>
### 第 40 行

```python
#: 先按服务端身份筛可见文档再检索；不能搜完整库后让模型决定权限。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：先按服务端身份筛可见文档再检索；不能搜完整库后让模型决定权限。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L41"></a>
### 第 41 行

```python
@app.post("/api/search")
```

**语法与数据变化：** 注册POST /api/search路由。

**为什么与边界：** POST允许带请求体，前端的method与路径必须匹配。

<a id="L42"></a>
### 第 42 行

```python
def retrieve(query: Query, tenant: str = Depends(identity)):
```

**语法与数据变化：** query由请求体构造，tenant通过Depends(identity)取得。

**为什么与边界：** 依赖失败会阻止处理器执行；不要让客户端直接指定任意tenant。

<a id="L43"></a>
### 第 43 行

```python
    visible = [doc for doc in load_documents(ROOT / "data/sample") if doc.id in ACL[tenant]]
```

**语法与数据变化：** 先加载手册，再仅保留ACL允许的文档。

**为什么与边界：** 检索输入已过滤，因此不可见文档连候选都不应出现；生产大库不能每次全量读文件，需要更合适存储。

<a id="L44"></a>
### 第 44 行

```python
    return [asdict(hit) for hit in search(query.question, visible, query.k)]
```

**语法与数据变化：** 调用检索器并asdict转换每条结果。

**为什么与边界：** 这只是候选证据输出，没有调用生成模型；JSON合法与证据充分不同。

<a id="L45"></a>
### 第 45 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L46"></a>
### 第 46 行

```python
#: 演示 SSE 帧格式，不是 LLM token 流；先完成检索再发 evidence 和 done 两个事件。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：演示 SSE 帧格式，不是 LLM token 流；先完成检索再发 evidence 和 done 两个事件。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L47"></a>
### 第 47 行

```python
@app.post("/api/events")
```

**语法与数据变化：** 注册另一个POST接口/api/events用于SSE格式演示。

**为什么与边界：** 路径不同于普通JSON接口，客户端需要对应的流消费逻辑。

<a id="L48"></a>
### 第 48 行

```python
def events(query: Query, tenant: str = Depends(identity)):
```

**语法与数据变化：** 事件处理器仍要求同样的Query与身份依赖。

**为什么与边界：** 流式输出不能成为绕开权限校验的另一个入口。

<a id="L49"></a>
### 第 49 行

```python
    hits = retrieve(query, tenant)
```

**语法与数据变化：** 先同步完成retrieve得到完整hits。

**为什么与边界：** 因此后面分帧发送不意味着模型正在逐token推理；首事件前检索已完成。

<a id="L50"></a>
### 第 50 行

```python
    def stream():
```

**语法与数据变化：** 定义局部生成器stream，执行时逐次yield帧。

**为什么与边界：** 函数定义本身不立即发送数据，StreamingResponse随后消费它。

<a id="L51"></a>
### 第 51 行

```python
        yield "event: evidence\ndata: " + json.dumps(hits, ensure_ascii=False) + "\n\n"
```

**语法与数据变化：** yield带event名称、JSON data以及双换行的SSE帧。

**为什么与边界：** 双换行结束一条事件；必须保持协议格式，不直接把任意换行文本拼成多条事件。

<a id="L52"></a>
### 第 52 行

```python
        yield 'event: done\ndata: {}\n\n'
```

**语法与数据变化：** 再yield done事件，用空对象标记结束。

**为什么与边界：** done是本应用的约定事件，不是模型输出内容。

<a id="L53"></a>
### 第 53 行

```python
    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})
```

**语法与数据变化：** 用StreamingResponse包装生成器，声明text/event-stream并禁止缓存。

**为什么与边界：** 这不提供断线重放、事件ID或真正LLM增量生成，生产还需连接管理。

<a id="L54"></a>
### 第 54 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L55"></a>
### 第 55 行

```python
#: 静态挂载在 API 路由之后；前端 fetch 相对路径，同源无需宽泛开放 CORS。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：静态挂载在 API 路由之后；前端 fetch 相对路径，同源无需宽泛开放 CORS。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L56"></a>
### 第 56 行

```python
app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")
```

**语法与数据变化：** 在API路由之后挂载frontend目录到根路径，html=True支持入口页。

**为什么与边界：** 顺序避免根挂载先吞掉API路由；只暴露前端目录，相对/api路径无需泛开放CORS。

## 跟一遍数据与验证边界

Alice(alpha)可以查Webhook，Bob(beta)只能看工单。Bob问Webhook应是200空列表，不是401；无效身份才401，关闭演示则503。

## 只练一个关键点（不是新的学习验收记录）

1. 运行 tests/test_api.py，分别找503、401、422和200空列表断言。
2. 按Alice/Bob×Webhook/工单画2×2授权结果表，与服务端ACL对应。
3. **复盘：** 身份失败为何不能当检索空结果？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
