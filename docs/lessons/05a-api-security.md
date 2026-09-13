# 5A · FastAPI、授权边界与 SSE

[全部课程](../course/index.md) · [上一课](04b-rerank-multiquery.md) · [下一课](05b-typescript-ui.md)

- **前置理解：** 阶段 4；先理解离线结果，再服务化
- **验证状态：** 真实 API/TestClient 已测；公开固定令牌仅用于虚构资料。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

> **预览兼容性更新：** 浏览器现用 `X-Demo-Token` 传递公开演示身份，避免与宿主的 `Authorization` 处理冲突；旧 CLI 的 Bearer 示例仍兼容。此机制只在 `EVIDENCEDESK_DEMO=1` 下生效，不是生产认证，也绝不能拿真实模型 Key 代替。

## 1. 问题：现在为什么需要它？

多个支持人员同时使用时，不同人不能看到同一套全部文档。将 search 包成接口还不够：身份必须由服务端确定，权限过滤必须先于检索和引用展示。

## 2. 原理：在这个问题里理解技术

请求 schema 限制类型和长度；认证判断是谁，授权判断能看什么。示例固定令牌映射到租户用于测试，默认关闭，绝不能用真实资料。生产应验证 OIDC/JWT 的签名、issuer、audience、到期与角色，不能相信用户自报 tenant。

SSE 用 event/data 和空行分帧。本例一次发 evidence 再发 done，不假装生成 token 流。真正流式 LLM 还需上游取消、背压、超时、错误帧和代理缓冲配置。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `src/evidencedesk/api.py`

完整源文件：[打开源码](../../src/evidencedesk/api.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

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

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–12 | 真实 FastAPI 接口，但只服务虚构手册；固定演示令牌不是生产身份体系。 |
| 13–18 | 此源码布局依赖 editable install 和仓库目录；不能把单独 wheel 当完整部署包。 |
| 19–23 | 演示专用头避开预览代理可能占用的 Authorization；仅显式启用虚构演示时生效。 |
| 24–30 | 专用头存在时只校验该值，不因它无效就回退；Bearer 保留给旧 CLI 示例。 |
| 31–39 | 限制输入长度和 k；strict 防止 True 或字符串被自动转换成整数。 |
| 40–45 | 先按服务端身份筛可见文档再检索；不能搜完整库后让模型决定权限。 |
| 46–54 | 演示 SSE 帧格式，不是 LLM token 流；先完成检索再发 evidence 和 done 两个事件。 |
| 55–56 | 静态挂载在 API 路由之后；前端 fetch 相对路径，同源无需宽泛开放 CORS。 |

### `tests/test_api.py`

完整源文件：[打开源码](../../tests/test_api.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

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

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 31–43 | 浏览器的专用演示头必须保持双向 ACL，而不是遇到 401 就关闭身份检查。 |
| 44–57 | 无效专用头不回退到另一套凭据；关闭演示模式时，两种头都不能启用接口。 |
| 58–83 | 模拟代理剥离 Authorization，验证专用头仍可用；这不是对真实代理行为的直接观测。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m pip install -e ".[web,dev]"
python -m pytest tests/test_api.py -q
# 只在演示虚构数据时启用；Windows PowerShell: $env:EVIDENCEDESK_DEMO="1"
export EVIDENCEDESK_DEMO=1
uvicorn evidencedesk.api:app --host 0.0.0.0 --port 8000
```

### 只做这些关键改动

1. 先不设演示变量，验证 /health 可用，而 /api/search 返回 503。
2. 启用演示后，在 /docs 用 Bearer demo-alice 搜“工单”，预期 []。用 demo-bob 搜同题，应命中 incident-escalation。
3. 无 token 应 401，k=true 应 422。
4. 在测试中添加一条“Bob 搜密钥返回 []”，防止只测试单向隔离。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

越权结果不应出现在候选、日志或缓存中，而非仅前端不显示。当前目录使用源码布局，不是可独立运行的 wheel；访问 /docs 可在前端未编译时测试 API。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 为什么“在提示里告诉模型别泄露”不能代替 ACL？若恶意文档要求打印密钥，哪些设计能阻止实际泄露？

**产出：** 可测试 API、双向 ACL 用例、威胁模型初稿。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://fastapi.tiangolo.com/tutorial/security/
- https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。
