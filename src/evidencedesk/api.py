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
