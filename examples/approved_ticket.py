#: 内存 SQLite 不会创建真实工单或保存客户资料。
import sqlite3
from evidencedesk.tickets import Approval, payload_hash, submit

#: 先证明拒绝路径，再模拟人工批准；演示不是公网审批接口。
def main():
    conn = sqlite3.connect(":memory:")
    draft = {"title": "Webhook 投递失败", "priority": "P1"}
    try:
        submit(conn, "alpha", "alice", "request-1", draft, None)
    except PermissionError:
        print("PASS: 未审批的写入被拒绝")
    #: 生产中这一对象必须从受保护记录读取，并检查审批过期、撤回和用户权限。
    approval = Approval("alpha", "alice", payload_hash(draft))
    first = submit(conn, "alpha", "alice", "request-1", draft, approval)
    second = submit(conn, "alpha", "alice", "request-1", draft, approval)
    assert first == second
    print("PASS: 相同请求重试返回同一工单 ID")
    conn.close()

if __name__ == "__main__":
    main()
