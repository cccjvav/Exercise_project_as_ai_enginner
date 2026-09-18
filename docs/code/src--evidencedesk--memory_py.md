# 有同意、隔离和到期规则的偏好记忆：逐行精讲

[精讲总目录](index.md) · [对应源码](../../src/evidencedesk/memory.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

只保存明确允许的语言偏好，演示如何按租户/用户隔离、过期和删除。

### 输入、输出与调用关系

PreferenceMemory实例持有records；save写入语言与截止时间，get返回语言或None，forget删除一项。时间由调用者注入。

### 运行与风险边界

`python -m examples.memory_lifecycle`，纯内存离线实验。

不是知识库或任意聊天历史存储，不持久化；本示例不严格校验全部参数类型，生产还要控制时间来源、鉴权和副本清理。

## 完整源码

<!-- source: src/evidencedesk/memory.py -->
```python
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
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
#: 记忆不是事实知识库；只保存定义好的语言偏好，避免把任意文本当长期指令。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：记忆不是事实知识库；只保存定义好的语言偏好，避免把任意文本当长期指令。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```python
from dataclasses import dataclass, field
```

**语法与数据变化：** 从 `dataclasses` 导入 `dataclass, field`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** 数据类工具。dataclass 自动生成初始化及比较等方法，asdict 转字典，field 控制字段默认值；普通字段类型注解不自动验证输入。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L4"></a>
### 第 4 行

```python
#: default_factory 防止不同实例共享同一个可变字典。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：default_factory 防止不同实例共享同一个可变字典。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L5"></a>
### 第 5 行

```python
@dataclass
```

**语法与数据变化：** dataclass装饰器为类生成初始化方法等。

**为什么与边界：** 这里没有frozen，因为records要更新；允许更新不等于可绕过同意和用户隔离。

<a id="L6"></a>
### 第 6 行

```python
class PreferenceMemory:
```

**语法与数据变化：** 定义一个内存偏好容器，不是语言模型自动学习出的参数。

**为什么与边界：** 每个实例有自己的数据生命周期，进程退出或实例丢弃会失去记录。

<a id="L7"></a>
### 第 7 行

```python
    records: dict = field(default_factory=dict)
```

**语法与数据变化：** field(default_factory=dict) 在每次实例化时新建字典。

**为什么与边界：** 不能把可变字典当成共享默认值，否则不同实例可能意外共享用户记录。

<a id="L8"></a>
### 第 8 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L9"></a>
### 第 9 行

```python
    #: 必须明确同意；now 参数可注入，让到期测试不依赖 sleep。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：必须明确同意；now 参数可注入，让到期测试不依赖 sleep。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L10"></a>
### 第 10 行

```python
    def save(self, tenant: str, user: str, language: str, consent: bool, now: float, ttl: float):
```

**语法与数据变化：** save 接收租户、用户、语言、同意标志、当前时间和寿命。

**为什么与边界：** 时间参数注入让测试无需sleep，但生产调用方必须提供可信时间与身份，不能相信客户端随意填写。

<a id="L11"></a>
### 第 11 行

```python
        if consent is not True:
```

**语法与数据变化：** 用 is not True 要求明确的布尔True，而不只是“真值”。

**为什么与边界：** 1、非空字符串等即使truthy也不应被当成同意。

<a id="L12"></a>
### 第 12 行

```python
            raise PermissionError("需要明确同意")
```

**语法与数据变化：** 没有明确同意就抛PermissionError，写入尚未发生。

**为什么与边界：** 拒绝应在副作用之前，不能先保存再检查。

<a id="L13"></a>
### 第 13 行

```python
        if language not in ("zh-CN", "en") or ttl <= 0:
```

**语法与数据变化：** 语言只允许zh-CN/en，且ttl>0。

**为什么与边界：** 这是范围规则，不是完整类型校验；任意长文本不应作为偏好注入持久指令。

<a id="L14"></a>
### 第 14 行

```python
            raise ValueError("只允许已定义的语言偏好和正 TTL")
```

**语法与数据变化：** 参数不合约定抛ValueError。

**为什么与边界：** 调用者应修正输入，不能把它伪装成“保存成功但为空”。

<a id="L15"></a>
### 第 15 行

```python
        self.records[(tenant, user)] = (language, now + ttl)
```

**语法与数据变化：** 用(tenant,user)元组做联合键，值为(language,now+ttl)。

**为什么与边界：** 同名用户跨租户不会共用键；覆盖已有键会更新语言和到期时间，没有追加无限历史。

<a id="L16"></a>
### 第 16 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L17"></a>
### 第 17 行

```python
    #: 读时检查过期，返回前就做租户与用户隔离；不是取出后再让模型过滤。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：读时检查过期，返回前就做租户与用户隔离；不是取出后再让模型过滤。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L18"></a>
### 第 18 行

```python
    def get(self, tenant: str, user: str, now: float):
```

**语法与数据变化：** get同样接收身份和时间，返回有效偏好或None。

**为什么与边界：** 不调用模型猜测用户身份，也不先取所有人的记录再筛选。

<a id="L19"></a>
### 第 19 行

```python
        key = (tenant, user)
```

**语法与数据变化：** 构造与save完全相同的联合键。

**为什么与边界：** 少一个tenant维度会造成跨租户碰撞，所以字段次序与保存端必须一致。

<a id="L20"></a>
### 第 20 行

```python
        item = self.records.get(key)
```

**语法与数据变化：** dict.get取记录，不存在返回None而非KeyError。

**为什么与边界：** 它不会创建默认语言或自动把用户偏好持久化。

<a id="L21"></a>
### 第 21 行

```python
        if item is None:
```

**语法与数据变化：** 显式区分没有记录的情况。

**为什么与边界：** None表示缺失，不应与允许值中的某个语言字符串混用。

<a id="L22"></a>
### 第 22 行

```python
            return None
```

**语法与数据变化：** 无记录直接返回None。

**为什么与边界：** 后续调用者可应用自己的默认语言，但那不是从记忆中读到的值。

<a id="L23"></a>
### 第 23 行

```python
        if now >= item[1]:
```

**语法与数据变化：** 比较now与截止时间，等于截止时间也算过期。

**为什么与边界：** 边界用>=，否则恰好到期时会多保留一次。

<a id="L24"></a>
### 第 24 行

```python
            self.records.pop(key)
```

**语法与数据变化：** 读取到过期项时顺便删除，避免继续返回旧偏好。

**为什么与边界：** 这是惰性清理，未被访问的过期记录仍可能留在字典里，不能冒充定时全量清理。

<a id="L25"></a>
### 第 25 行

```python
            return None
```

**语法与数据变化：** 过期分支返回None，停止读取。

**为什么与边界：** 不会返回刚删除项里的旧language。

<a id="L26"></a>
### 第 26 行

```python
        return item[0]
```

**语法与数据变化：** 有效记录返回元组首项语言，不返回时间与整个字典。

**为什么与边界：** 缩小数据暴露范围，调用者只拿到需要的偏好。

<a id="L27"></a>
### 第 27 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L28"></a>
### 第 28 行

```python
    #: 删除幂等；真实系统还需清理向量索引、缓存、备份及保留期内日志副本。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：删除幂等；真实系统还需清理向量索引、缓存、备份及保留期内日志副本。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L29"></a>
### 第 29 行

```python
    def forget(self, tenant: str, user: str):
```

**语法与数据变化：** 定义显式删除接口，仍按租户和用户定位。

**为什么与边界：** 业务上谁能调用应在可信服务层授权；此函数本身没有认证流程。

<a id="L30"></a>
### 第 30 行

```python
        self.records.pop((tenant, user), None)
```

**语法与数据变化：** pop的默认值None让键不存在也不报错。

**为什么与边界：** 删除幂等只覆盖此内存字典；真实系统的缓存、索引、备份和日志仍需清理策略。

## 跟一遍数据与验证边界

在now=100以ttl=10保存zh-CN，109可读、110过期；另一个租户同名用户不可读。删除不存在的键不报错，使重复删除安全。

## 只练一个关键点（不是新的学习验收记录）

1. 运行记忆示例，手算now=100、ttl=60的到期边界。
2. 固定身份，分别检查159/160及forget后201；只使用虚构偏好。
3. **复盘：** 惰性删除为什么不代表所有存储副本已删除？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
