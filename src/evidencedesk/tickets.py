#: SQLite 模拟工单写入；生产外部 API 还需 outbox、远端幂等键及重试策略。
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from uuid import uuid4

#: Approval 只能由可信服务从受保护审批记录构造，绝不能反序列化客户端自报批准。
@dataclass(frozen=True)
class Approval:
    tenant: str
    user: str
    payload_hash: str

#: 按键排序后再哈希，字段顺序不同不影响审批绑定，内容变了则必须重新审批。
def payload_hash(payload: dict) -> str:
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

#: 身份与当前 payload 都匹配才允许进入写路径；拒绝不能晚于写操作。
def submit(conn: sqlite3.Connection, tenant: str, user: str, key: str,
           payload: dict, approval: Approval | None) -> str:
    digest = payload_hash(payload)
    if approval != Approval(tenant, user, digest):
        raise PermissionError("缺少与身份、当前草稿一致的可信审批")
    if set(payload) != {"title", "priority"} or not isinstance(payload["title"], str) or not 1 <= len(payload["title"].strip()) <= 120:
        raise ValueError("工单字段无效")
    if payload["priority"] not in ("P1", "P3") or not key:
        raise ValueError("优先级或幂等键无效")
    #: 参数占位符避免 SQL 拼接注入；唯一约束由数据库执行，事务内处理冲突。
    with conn:
        conn.execute("CREATE TABLE IF NOT EXISTS tickets (tenant TEXT, key TEXT, digest TEXT, id TEXT, PRIMARY KEY (tenant,key))")
        conn.execute("INSERT OR IGNORE INTO tickets VALUES (?,?,?,?)", (tenant, key, digest, str(uuid4())))
        row = conn.execute("SELECT digest,id FROM tickets WHERE tenant=? AND key=?", (tenant, key)).fetchone()
        if row[0] != digest:
            raise ValueError("同一个幂等键不能用于不同内容")
    return row[1]
