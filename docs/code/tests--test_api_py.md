# API身份、ACL与代理情形的回归：逐行精讲

[精讲总目录](index.md) · [对应源码](../../tests/test_api.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

用进程内HTTP请求检查默认关闭、两个演示身份的双向隔离和SSE协议，并模拟一种代理行为。

### 输入、输出与调用关系

TestClient调用FastAPI；环境由monkeypatch恢复，不起公网服务。

### 运行与风险边界

`python -m pytest tests/test_api.py -q -rs`，需要fastapi/httpx及项目依赖。

演示token不是生产认证。模拟剥离Authorization不是观察真实代理；本地测试通过不等于用户浏览器401已经确认消失。

## 完整源码

<!-- source: tests/test_api.py -->
```python
import pytest
pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient
from evidencedesk.api import app

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("EVIDENCEDESK_DEMO", "1")
    with TestClient(app) as client:
        yield client

def test_health_and_default_closed(client, monkeypatch):
    assert client.get("/health").status_code == 200
    monkeypatch.delenv("EVIDENCEDESK_DEMO")
    assert client.post("/api/search", json={"question": "工单"}).status_code == 503

def test_auth_acl_and_sse(client):
    payload = {"question": "工单", "k": 3}
    assert client.post("/api/search", json=payload).status_code == 401
    a = {"Authorization": "Bearer demo-alice"}
    b = {"Authorization": "Bearer demo-bob"}
    assert client.post("/api/search", json=payload, headers=a).json() == []
    assert client.post("/api/search", json=payload, headers=b).json()[0]["document_id"] == "incident-escalation"
    stream = client.post("/api/events", json=payload, headers=b)
    assert stream.headers["content-type"].startswith("text/event-stream")
    assert "event: evidence\n" in stream.text and stream.text.endswith('event: done\ndata: {}\n\n')
    for k in [0, True, "3", 11]:
        assert client.post("/api/search", json={"question": "工单", "k": k}, headers=b).status_code == 422

#: 浏览器的专用演示头必须保持双向 ACL，而不是遇到 401 就关闭身份检查。
@pytest.mark.parametrize("token,query,ids", [
    ("demo-alice", "Webhook", ["webhook-delivery"]),
    ("demo-bob", "Webhook", []),
    ("demo-bob", "工单", ["incident-escalation"]),
    ("demo-alice", "工单", []),
])
def test_demo_header_acl(client, token, query, ids):
    response = client.post("/api/search", headers={"X-Demo-Token": token}, json={"question": query})
    assert response.status_code == 200
    assert [hit["document_id"] for hit in response.json()] == ids


#: 无效专用头不回退到另一套凭据；关闭演示模式时，两种头都不能启用接口。
@pytest.mark.parametrize("token", ["", "unknown", "Bearer demo-alice"])
def test_invalid_demo_header_does_not_fall_back(client, token):
    response = client.post("/api/search", headers={"X-Demo-Token": token, "Authorization": "Bearer demo-alice"},
                           json={"question": "Webhook"})
    assert response.status_code == 401


def test_demo_header_still_requires_explicit_mode(client, monkeypatch):
    monkeypatch.delenv("EVIDENCEDESK_DEMO")
    response = client.post("/api/search", headers={"X-Demo-Token": "demo-alice"}, json={"question": "Webhook"})
    assert response.status_code == 503


#: 模拟代理剥离 Authorization，验证专用头仍可用；这不是对真实代理行为的直接观测。
def test_preview_transport_with_authorization_stripped(monkeypatch):
    # Model the suspected proxy behavior, without claiming this observes the real proxy.
    class StripAuthorization:
        def __init__(self, wrapped):
            self.wrapped = wrapped

        async def __call__(self, scope, receive, send):
            if scope["type"] == "http":
                scope = {**scope, "headers": [(k, v) for k, v in scope["headers"] if k.lower() != b"authorization"]}
            await self.wrapped(scope, receive, send)

    monkeypatch.setenv("EVIDENCEDESK_DEMO", "1")
    with TestClient(StripAuthorization(app)) as proxied:
        payload = {"question": "Webhook"}
        assert proxied.post("/api/search", headers={"Authorization": "Bearer demo-alice"}, json=payload).status_code == 401
        response = proxied.post("/api/search", headers={"X-Demo-Token": "demo-alice"}, json=payload)
        assert response.status_code == 200 and response.json()[0]["document_id"] == "webhook-delivery"
        events = proxied.post("/api/events", headers={"X-Demo-Token": "demo-alice"}, json=payload)
        assert events.status_code == 200 and "event: evidence" in events.text


def test_proxy_authorization_can_coexist_with_demo_header(client):
    response = client.post("/api/search", headers={"Authorization": "Bearer proxy-owned-placeholder", "X-Demo-Token": "demo-bob"},
                           json={"question": "工单"})
    assert response.status_code == 200 and response.json()[0]["document_id"] == "incident-escalation"
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
import pytest
```

**语法与数据变化：** 导入 `pytest` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 测试框架。装饰器展开用例，raises 检查预期异常，fixture 提供隔离资源；测试通过仅覆盖所写的条件。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L2"></a>
### 第 2 行

```python
pytest.importorskip("fastapi")
```

**语法与数据变化：** 缺fastapi则跳过整个测试模块。

**为什么与边界：** 不是应用启动成功的证明。

<a id="L3"></a>
### 第 3 行

```python
pytest.importorskip("httpx")
```

**语法与数据变化：** 缺httpx也跳过，因为TestClient需要它。

**为什么与边界：** 查看-rs区分skip和pass。

<a id="L4"></a>
### 第 4 行

```python
from fastapi.testclient import TestClient
```

**语法与数据变化：** 从 `fastapi.testclient` 导入 `TestClient`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 进程内 HTTP 测试客户端。通过 ASGI 调用应用，能验证路由契约，但不是浏览器端到端或真实网络代理测试。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

```python
from evidencedesk.api import app
```

**语法与数据变化：** 从 `evidencedesk.api` 导入 `app`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** app是已注册路由的FastAPI对象，TestClient可进程内调用；导入不启动uvicorn，但顶层静态目录等配置会建立。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L7"></a>
### 第 7 行

```python
@pytest.fixture
```

**语法与数据变化：** fixture装饰器把下面函数注册为可注入client。

**为什么与边界：** 测试参数名与fixture名对应。

<a id="L8"></a>
### 第 8 行

```python
def client(monkeypatch):
```

**语法与数据变化：** monkeypatch由pytest提供，用来临时修改环境。

**为什么与边界：** 每个用例独立启用演示模式，不污染真实运行配置。

<a id="L9"></a>
### 第 9 行

```python
    monkeypatch.setenv("EVIDENCEDESK_DEMO", "1")
```

**语法与数据变化：** 设置显式演示开关为1。

**为什么与边界：** API默认关闭；测试中开放不是修改生产默认值。

<a id="L10"></a>
### 第 10 行

```python
    with TestClient(app) as client:
```

**语法与数据变化：** 用TestClient上下文管理应用生命周期。

**为什么与边界：** 调用ASGI而非真实浏览器网络代理。

<a id="L11"></a>
### 第 11 行

```python
        yield client
```

**语法与数据变化：** yield把client交给测试，测试后返回上下文清理。

**为什么与边界：** 不同于return，yield之后可完成资源退出。

<a id="L12"></a>
### 第 12 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L13"></a>
### 第 13 行

```python
def test_health_and_default_closed(client, monkeypatch):
```

**语法与数据变化：** 测试健康检查与业务默认关闭。

**为什么与边界：** 健康可访问不意味着检索端点应该匿名开放。

<a id="L14"></a>
### 第 14 行

```python
    assert client.get("/health").status_code == 200
```

**语法与数据变化：** /health应200。

**为什么与边界：** 仅说明该路由能处理请求，不证明数据库/模型可用。

<a id="L15"></a>
### 第 15 行

```python
    monkeypatch.delenv("EVIDENCEDESK_DEMO")
```

**语法与数据变化：** 删除刚由fixture设置的演示开关。

**为什么与边界：** 模拟默认/关闭环境，不更改源码常量。

<a id="L16"></a>
### 第 16 行

```python
    assert client.post("/api/search", json={"question": "工单"}).status_code == 503
```

**语法与数据变化：** 关闭时业务POST应503。

**为什么与边界：** 不是把缺模式伪装成无答案空列表。

<a id="L17"></a>
### 第 17 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L18"></a>
### 第 18 行

```python
def test_auth_acl_and_sse(client):
```

**语法与数据变化：** 组合验证Bearer、ACL、SSE及输入校验。

**为什么与边界：** 每个断言对应不同接口契约。

<a id="L19"></a>
### 第 19 行

```python
    payload = {"question": "工单", "k": 3}
```

**语法与数据变化：** 构造工单查询、k3。

**为什么与边界：** 同一输入给不同身份才可比较可见范围。

<a id="L20"></a>
### 第 20 行

```python
    assert client.post("/api/search", json=payload).status_code == 401
```

**语法与数据变化：** 不带身份应401。

**为什么与边界：** 正常选中演示用户应带头，401不能解读为没有候选。

<a id="L21"></a>
### 第 21 行

```python
    a = {"Authorization": "Bearer demo-alice"}
```

**语法与数据变化：** 为Alice构造Bearer头。

**为什么与边界：** 这是公开演示身份，不是秘密生产凭据。

<a id="L22"></a>
### 第 22 行

```python
    b = {"Authorization": "Bearer demo-bob"}
```

**语法与数据变化：** 为Bob构造另一身份头。

**为什么与边界：** 两个身份看到的文档集合不同。

<a id="L23"></a>
### 第 23 行

```python
    assert client.post("/api/search", json=payload, headers=a).json() == []
```

**语法与数据变化：** Alice查询工单应得到空列表。

**为什么与边界：** 说明授权后候选为空，不是认证失败；此行未独立断言status。

<a id="L24"></a>
### 第 24 行

```python
    assert client.post("/api/search", json=payload, headers=b).json()[0]["document_id"] == "incident-escalation"
```

**语法与数据变化：** Bob应拿到incident-escalation。

**为什么与边界：** 同时防止“把所有用户结果清空”伪装成ACL安全。

<a id="L25"></a>
### 第 25 行

```python
    stream = client.post("/api/events", json=payload, headers=b)
```

**语法与数据变化：** 向事件端点发送同样Bob查询。

**为什么与边界：** 此SSE流输出既有检索结果，不是模型逐token生成。

<a id="L26"></a>
### 第 26 行

```python
    assert stream.headers["content-type"].startswith("text/event-stream")
```

**语法与数据变化：** content-type必须以text/event-stream开头。

**为什么与边界：** 允许额外charset等参数，不要求整个头逐字相等。

<a id="L27"></a>
### 第 27 行

```python
    assert "event: evidence\n" in stream.text and stream.text.endswith('event: done\ndata: {}\n\n')
```

**语法与数据变化：** 流需含evidence事件并以done空数据帧结束。

**为什么与边界：** 检查事件帧和双换行结束约定，未覆盖浏览器断流重连。

<a id="L28"></a>
### 第 28 行

```python
    for k in [0, True, "3", 11]:
```

**语法与数据变化：** 逐个测试0、布尔、字符串3和超上限11。

**为什么与边界：** 强调严格整数与1–10边界。

<a id="L29"></a>
### 第 29 行

```python
        assert client.post("/api/search", json={"question": "工单", "k": k}, headers=b).status_code == 422
```

**语法与数据变化：** 每种无效k应422。

**为什么与边界：** Pydantic拒绝输入，不能默默转换布尔或字符串后执行。

<a id="L30"></a>
### 第 30 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L31"></a>
### 第 31 行

```python
#: 浏览器的专用演示头必须保持双向 ACL，而不是遇到 401 就关闭身份检查。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：浏览器的专用演示头必须保持双向 ACL，而不是遇到 401 就关闭身份检查。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L32"></a>
### 第 32 行

```python
@pytest.mark.parametrize("token,query,ids", [
```

**语法与数据变化：** 参数化专用演示头下的双向ACL。

**为什么与边界：** 四个用例分别覆盖允许与禁止，避免只测一个身份。

<a id="L33"></a>
### 第 33 行

```python
    ("demo-alice", "Webhook", ["webhook-delivery"]),
```

**语法与数据变化：** Alice对Webhook应有其文档。

**为什么与边界：** 这是允许路径，排除全面拒绝的假安全。

<a id="L34"></a>
### 第 34 行

```python
    ("demo-bob", "Webhook", []),
```

**语法与数据变化：** Bob对Webhook应为空。

**为什么与边界：** 同问题不同身份，隔离方向之一。

<a id="L35"></a>
### 第 35 行

```python
    ("demo-bob", "工单", ["incident-escalation"]),
```

**语法与数据变化：** Bob对工单应有升级文档。

**为什么与边界：** 验证另一个身份的合法能力。

<a id="L36"></a>
### 第 36 行

```python
    ("demo-alice", "工单", []),
```

**语法与数据变化：** Alice对工单应为空。

**为什么与边界：** 隔离反方向不能遗漏。

<a id="L37"></a>
### 第 37 行

```python
])
```

**语法与数据变化：** 闭合四个参数组。

**为什么与边界：** ids是每组完整预期列表，不只预期首条。

<a id="L38"></a>
### 第 38 行

```python
def test_demo_header_acl(client, token, query, ids):
```

**语法与数据变化：** 接收client和当前token/query/ids。

**为什么与边界：** pytest将装饰器与fixture合并注入。

<a id="L39"></a>
### 第 39 行

```python
    response = client.post("/api/search", headers={"X-Demo-Token": token}, json={"question": query})
```

**语法与数据变化：** 用X-Demo-Token发送请求。

**为什么与边界：** 浏览器走专用头，兼容代理可能占用Authorization的情形。

<a id="L40"></a>
### 第 40 行

```python
    assert response.status_code == 200
```

**语法与数据变化：** 要求HTTP200。

**为什么与边界：** 认证错误不能被误当空候选，先查status再查内容。

<a id="L41"></a>
### 第 41 行

```python
    assert [hit["document_id"] for hit in response.json()] == ids
```

**语法与数据变化：** 提取所有返回文档ID并与完整ids比较。

**为什么与边界：** 既检查缺失也检查额外泄漏，不只验证第一条正确。

<a id="L42"></a>
### 第 42 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L43"></a>
### 第 43 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L44"></a>
### 第 44 行

```python
#: 无效专用头不回退到另一套凭据；关闭演示模式时，两种头都不能启用接口。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：无效专用头不回退到另一套凭据；关闭演示模式时，两种头都不能启用接口。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L45"></a>
### 第 45 行

```python
@pytest.mark.parametrize("token", ["", "unknown", "Bearer demo-alice"])
```

**语法与数据变化：** 三种非法专用头：空、未知、错误Bearer前缀。

**为什么与边界：** 专用头约定只填token，不能混用Authorization语法。

<a id="L46"></a>
### 第 46 行

```python
def test_invalid_demo_header_does_not_fall_back(client, token):
```

**语法与数据变化：** 定义无效专用头不得回退测试。

**为什么与边界：** 防止身份歧义或恶意把两套凭据叠加。

<a id="L47"></a>
### 第 47 行

```python
    response = client.post("/api/search", headers={"X-Demo-Token": token, "Authorization": "Bearer demo-alice"},
```

**语法与数据变化：** 同时放无效专用头和合法Alice Bearer。

**为什么与边界：** 故意提供可回退凭据，才能发现错误fallback。

<a id="L48"></a>
### 第 48 行

```python
                           json={"question": "Webhook"})
```

**语法与数据变化：** 给合法Webhook查询，闭合请求。

**为什么与边界：** 输入合法，失败应聚焦身份优先级。

<a id="L49"></a>
### 第 49 行

```python
    assert response.status_code == 401
```

**语法与数据变化：** 结果必须401。

**为什么与边界：** 不能因为另一套头可用而忽略已经显式给出的无效专用头。

<a id="L50"></a>
### 第 50 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L51"></a>
### 第 51 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L52"></a>
### 第 52 行

```python
def test_demo_header_still_requires_explicit_mode(client, monkeypatch):
```

**语法与数据变化：** 专用头也必须服从显式演示模式。

**为什么与边界：** 新增头不应成为绕过默认关闭的旁路。

<a id="L53"></a>
### 第 53 行

```python
    monkeypatch.delenv("EVIDENCEDESK_DEMO")
```

**语法与数据变化：** 删除演示环境变量。

**为什么与边界：** 此用例随后身份有效但模式关闭。

<a id="L54"></a>
### 第 54 行

```python
    response = client.post("/api/search", headers={"X-Demo-Token": "demo-alice"}, json={"question": "Webhook"})
```

**语法与数据变化：** 发送合法专用token与查询。

**为什么与边界：** 不混入其他非法条件。

<a id="L55"></a>
### 第 55 行

```python
    assert response.status_code == 503
```

**语法与数据变化：** 应503而不是200。

**为什么与边界：** 保护服务运行模式边界，不仅是token有效性。

<a id="L56"></a>
### 第 56 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L57"></a>
### 第 57 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L58"></a>
### 第 58 行

```python
#: 模拟代理剥离 Authorization，验证专用头仍可用；这不是对真实代理行为的直接观测。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：模拟代理剥离 Authorization，验证专用头仍可用；这不是对真实代理行为的直接观测。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L59"></a>
### 第 59 行

```python
def test_preview_transport_with_authorization_stripped(monkeypatch):
```

**语法与数据变化：** 模拟代理删除Authorization时的兼容性。

**为什么与边界：** 这是受控假设，不能当真实平台已被抓包证实。

<a id="L60"></a>
### 第 60 行

```python
    # Model the suspected proxy behavior, without claiming this observes the real proxy.
```

这是源码注释，不是执行语句。它提醒本段的设计意图：Model the suspected proxy behavior, without claiming this observes the real proxy. 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L61"></a>
### 第 61 行

```python
    class StripAuthorization:
```

**语法与数据变化：** 定义包裹ASGI应用的可调用类。

**为什么与边界：** 只供测试，不修改生产app本体。

<a id="L62"></a>
### 第 62 行

```python
        def __init__(self, wrapped):
```

**语法与数据变化：** 构造器接收被包装应用。

**为什么与边界：** self用于保存实例上的引用。

<a id="L63"></a>
### 第 63 行

```python
            self.wrapped = wrapped
```

**语法与数据变化：** 把应用存在self.wrapped以便转发。

**为什么与边界：** 不是复制应用数据或建立另一身份系统。

<a id="L64"></a>
### 第 64 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L65"></a>
### 第 65 行

```python
        async def __call__(self, scope, receive, send):
```

**语法与数据变化：** 异步__call__实现ASGI(scope,receive,send)接口。

**为什么与边界：** scope描述请求，receive/send是协议回调。

<a id="L66"></a>
### 第 66 行

```python
            if scope["type"] == "http":
```

**语法与数据变化：** 只对HTTP scope处理header。

**为什么与边界：** 生命周期等非HTTP事件应原样转发。

<a id="L67"></a>
### 第 67 行

```python
                scope = {**scope, "headers": [(k, v) for k, v in scope["headers"] if k.lower() != b"authorization"]}
```

**语法与数据变化：** 浅拷贝scope，过滤字节头名authorization，其余header保留。

**为什么与边界：** 不原地改共享scope；k是bytes所以与b"authorization"比较。

<a id="L68"></a>
### 第 68 行

```python
            await self.wrapped(scope, receive, send)
```

**语法与数据变化：** await原应用，使用修改后的scope与原回调。

**为什么与边界：** 模拟中间层转发，不自己伪造200响应。

<a id="L69"></a>
### 第 69 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L70"></a>
### 第 70 行

```python
    monkeypatch.setenv("EVIDENCEDESK_DEMO", "1")
```

**语法与数据变化：** 显式打开演示模式。

**为什么与边界：** 隔离代理行为，不让503掩盖身份问题。

<a id="L71"></a>
### 第 71 行

```python
    with TestClient(StripAuthorization(app)) as proxied:
```

**语法与数据变化：** 用包装应用创建TestClient。

**为什么与边界：** 请求确实先通过删头逻辑，而非只直接调用原app。

<a id="L72"></a>
### 第 72 行

```python
        payload = {"question": "Webhook"}
```

**语法与数据变化：** 设置固定Webhook问题。

**为什么与边界：** 两种身份头用相同输入比较。

<a id="L73"></a>
### 第 73 行

```python
        assert proxied.post("/api/search", headers={"Authorization": "Bearer demo-alice"}, json=payload).status_code == 401
```

**语法与数据变化：** 仅Authorization应被删掉，导致401。

**为什么与边界：** 确认模拟中间层实际生效，否则后面的专用头成功缺少对照。

<a id="L74"></a>
### 第 74 行

```python
        response = proxied.post("/api/search", headers={"X-Demo-Token": "demo-alice"}, json=payload)
```

**语法与数据变化：** 改用专用头请求。

**为什么与边界：** 模拟层不删此头，API应能识别身份。

<a id="L75"></a>
### 第 75 行

```python
        assert response.status_code == 200 and response.json()[0]["document_id"] == "webhook-delivery"
```

**语法与数据变化：** 要求200且首条Webhook文档。

**为什么与边界：** 同时检查认证通过和预期业务输出。

<a id="L76"></a>
### 第 76 行

```python
        events = proxied.post("/api/events", headers={"X-Demo-Token": "demo-alice"}, json=payload)
```

**语法与数据变化：** 事件端点也通过同一专用头请求。

**为什么与边界：** 不能只修普通搜索而遗漏SSE路径。

<a id="L77"></a>
### 第 77 行

```python
        assert events.status_code == 200 and "event: evidence" in events.text
```

**语法与数据变化：** 要求200并含证据事件。

**为什么与边界：** 本地协议验证，不代表真实浏览器跨代理流传输已验收。

<a id="L78"></a>
### 第 78 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L79"></a>
### 第 79 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L80"></a>
### 第 80 行

```python
def test_proxy_authorization_can_coexist_with_demo_header(client):
```

**语法与数据变化：** 验证代理自己的Authorization可与应用专用头共存。

**为什么与边界：** 应用应按明确优先级使用演示头，不解析成错误用户。

<a id="L81"></a>
### 第 81 行

```python
    response = client.post("/api/search", headers={"Authorization": "Bearer proxy-owned-placeholder", "X-Demo-Token": "demo-bob"},
```

**语法与数据变化：** 同时发代理占位Bearer与Bob专用token。

**为什么与边界：** 占位不是凭据，不包含任何实际平台秘密。

<a id="L82"></a>
### 第 82 行

```python
                           json={"question": "工单"})
```

**语法与数据变化：** 查询工单并闭合请求。

**为什么与边界：** Bob应具备对应演示权限。

<a id="L83"></a>
### 第 83 行

```python
    assert response.status_code == 200 and response.json()[0]["document_id"] == "incident-escalation"
```

**语法与数据变化：** 要求成功及工单文档。

**为什么与边界：** 证明专用头优先于另一用途的Authorization，而非在401时关闭检查。

## 跟一遍数据与验证边界

Alice可见Webhook不可见工单，Bob相反；无效专用头即使附合法Bearer也应401，不能为了消除401关闭鉴权。

## 只练一个关键点（不是新的学习验收记录）

1. 只运行 -k demo_header 用例，再运行 -k proxy 或 -k stripped 用例。
2. 指出包装类删掉的是哪一个头，并区分模拟观察与真实浏览器观察。
3. **复盘：** 修复代理兼容为什么不能降低身份/ACL检查？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
