#: 记忆不是事实知识库；只保存定义好的语言偏好，避免把任意文本当长期指令。
from dataclasses import dataclass, field

#: default_factory 防止不同实例共享同一个可变字典。
@dataclass
class PreferenceMemory:
    records: dict = field(default_factory=dict)

    #: 必须明确同意；now 参数可注入，让到期测试不依赖 sleep。
    def save(self, tenant: str, user: str, language: str, consent: bool, now: float, ttl: float):
        if consent is not True:
            raise PermissionError("需要明确同意")
        if language not in ("zh-CN", "en") or ttl <= 0:
            raise ValueError("只允许已定义的语言偏好和正 TTL")
        self.records[(tenant, user)] = (language, now + ttl)

    #: 读时检查过期，返回前就做租户与用户隔离；不是取出后再让模型过滤。
    def get(self, tenant: str, user: str, now: float):
        key = (tenant, user)
        item = self.records.get(key)
        if item is None:
            return None
        if now >= item[1]:
            self.records.pop(key)
            return None
        return item[0]

    #: 删除幂等；真实系统还需清理向量索引、缓存、备份及保留期内日志副本。
    def forget(self, tenant: str, user: str):
        self.records.pop((tenant, user), None)
