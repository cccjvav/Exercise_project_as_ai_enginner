#: 用固定时间测试，避免基于 sleep 的慢且不稳定测试。
from evidencedesk.memory import PreferenceMemory

#: 分别验证同意后读取、跨租户隔离、到期不可读和撤回删除。
def main():
    memory = PreferenceMemory()
    memory.save("alpha", "alice", "zh-CN", consent=True, now=100, ttl=60)
    assert memory.get("alpha", "alice", now=120) == "zh-CN"
    assert memory.get("beta", "alice", now=120) is None
    assert memory.get("alpha", "alice", now=160) is None
    memory.save("alpha", "alice", "en", consent=True, now=200, ttl=60)
    memory.forget("alpha", "alice")
    assert memory.get("alpha", "alice", now=201) is None
    print("PASS: 租户隔离、到期和撤回删除")

if __name__ == "__main__":
    main()
