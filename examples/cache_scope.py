#: 缓存键可能成为旁路权限漏洞；演示键设计，不假装已经连接 Redis。
import hashlib
import json

#: 用户、授权版本、索引版本与问题共同决定键；JSON 数组避免简单拼接冲突。
def cache_key(tenant: str, user: str, acl_version: str, index_version: str, query: str) -> str:
    payload = json.dumps([tenant, user, acl_version, index_version, query], ensure_ascii=False)
    return "answer:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

#: 相同问题跨用户不可复用缓存，ACL 改变后也不能继续命中旧授权结果。
def main():
    a = cache_key("alpha", "alice", "acl-v1", "index-v1", "重试")
    b = cache_key("beta", "bob", "acl-v1", "index-v1", "重试")
    assert a != b
    assert a != cache_key("alpha", "alice", "acl-v2", "index-v1", "重试")
    print("PASS: 用户、租户和授权版本改变都会隔离缓存键")

if __name__ == "__main__":
    main()
