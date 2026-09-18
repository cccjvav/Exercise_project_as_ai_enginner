# Agnes 的预算开关与响应契约测试：逐行精讲

[精讲总目录](index.md) · [对应源码](../../tests/test_agnes.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

用MockTransport截住所有HTTP请求，验证默认不调用、显式确认、单请求和输出检查。

### 输入、输出与调用关系

假Key、假HTTP响应→断言；绝不验证真实账号、价格或模型质量。

### 运行与风险边界

`python -m pytest tests/test_agnes.py -q -rs`，缺httpx会跳过整个模块。

mock中的回答是人工fixture，不能称作Agnes实际生成；测试也不是当前免费政策查询。

## 完整源码

<!-- source: tests/test_agnes.py -->
```python
"""Contract and budget-guard tests use a mock transport, NOT real model results."""
import json
import pytest
httpx = pytest.importorskip("httpx")
from evidencedesk.agnes import answer, prepare, validate_answer


def test_dry_run_never_calls_network():
    def forbidden(request):
        raise AssertionError("dry-run tried network")
    assert "dry-run" in answer("Webhook", transport=httpx.MockTransport(forbidden))["mode"]


def test_explicit_opt_in_and_missing_key(monkeypatch):
    monkeypatch.delenv("AGNES_API_KEY", raising=False)
    with pytest.raises(ValueError, match="免费"):
        answer("Webhook", live=True)
    with pytest.raises(ValueError, match="AGNES_API_KEY"):
        answer("Webhook", live=True, confirmed_current_free=True)


def test_one_request_and_no_key_in_result(monkeypatch):
    monkeypatch.setenv("AGNES_API_KEY", "test-only-not-a-real-key")
    calls = []
    def handler(request):
        calls.append(request)
        payload = json.loads(request.content)
        assert str(request.url) == "https://apihub.agnes-ai.com/v1/chat/completions"
        assert payload["model"] == "agnes-2.5-flash" and payload["max_tokens"] == 400
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({
            "answer": "最多重试 3 次，不包含首次投递。", "citation_ids": ["webhook-delivery"], "insufficient_evidence": False})}}]})
    result = answer("Webhook", live=True, confirmed_current_free=True, transport=httpx.MockTransport(handler))
    assert len(calls) == 1 and "test-only" not in json.dumps(result)


@pytest.mark.parametrize("status", [302, 401, 402, 429, 500])
def test_errors_no_retry_or_fallback(monkeypatch, status):
    monkeypatch.setenv("AGNES_API_KEY", "test-only")
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(status, headers={"Location": "https://example.com"}, text="sensitive error not logged")
    with pytest.raises(RuntimeError, match=f"HTTP {status}") as caught:
        answer("Webhook", live=True, confirmed_current_free=True, transport=httpx.MockTransport(handler))
    assert len(calls) == 1 and "sensitive" not in str(caught.value)


@pytest.mark.parametrize("value", [
    {"answer": "x", "citation_ids": ["missing"], "insufficient_evidence": False},
    {"answer": "x", "citation_ids": [], "insufficient_evidence": False},
    {"answer": "x", "citation_ids": ["webhook-delivery"], "insufficient_evidence": True},
    {"answer": "x", "citation_ids": [], "insufficient_evidence": "true"},
])
def test_invalid_output(value):
    with pytest.raises(ValueError):
        validate_answer(json.dumps(value), {"webhook-delivery"})


def test_no_matching_evidence_skips_model(monkeypatch):
    monkeypatch.setenv("AGNES_API_KEY", "test-only")
    def forbidden(request):
        raise AssertionError("should not call for empty candidates")
    assert answer("年付折扣是多少？", live=True, confirmed_current_free=True,
                  transport=httpx.MockTransport(forbidden))["mode"] == "no model call"


def test_input_limit():
    for question in ("", " " * 5, "a" * 1001):
        with pytest.raises(ValueError):
            prepare(question)
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
"""Contract and budget-guard tests use a mock transport, NOT real model results."""
```

**语法与数据变化：** 模块docstring明确mock和真实模型结果的区别。

**为什么与边界：** 测试命名再像在线调用，也必须检查transport实际指向哪里。

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
import pytest
```

**语法与数据变化：** 导入 `pytest` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 测试框架。装饰器展开用例，raises 检查预期异常，fixture 提供隔离资源；测试通过仅覆盖所写的条件。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

```python
httpx = pytest.importorskip("httpx")
```

**语法与数据变化：** importorskip尝试导入httpx并返回模块，缺包则跳过此文件。

**为什么与边界：** 跳过不等于适配器已经测试通过。

<a id="L5"></a>
### 第 5 行

```python
from evidencedesk.agnes import answer, prepare, validate_answer
```

**语法与数据变化：** 从 `evidencedesk.agnes` 导入 `answer, prepare, validate_answer`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** prepare准备公开证据与请求，validate_answer检查JSON/引用契约，answer默认dry-run；live仍需显式免费权益确认及配置。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L6"></a>
### 第 6 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L7"></a>
### 第 7 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L8"></a>
### 第 8 行

```python
def test_dry_run_never_calls_network():
```

**语法与数据变化：** 定义默认预演不联网的回归。

**为什么与边界：** 保护用户仅运行示例时不外发数据的承诺。

<a id="L9"></a>
### 第 9 行

```python
    def forbidden(request):
```

**语法与数据变化：** 定义禁止请求的transport handler。

**为什么与边界：** 这里只创建函数，真正请求到达才执行它。

<a id="L10"></a>
### 第 10 行

```python
        raise AssertionError("dry-run tried network")
```

**语法与数据变化：** 一旦调用handler立即AssertionError。

**为什么与边界：** 比只检查返回mode更能发现偷偷发起网络请求的实现。

<a id="L11"></a>
### 第 11 行

```python
    assert "dry-run" in answer("Webhook", transport=httpx.MockTransport(forbidden))["mode"]
```

**语法与数据变化：** 把禁止handler注入MockTransport，要求结果mode含dry-run。

**为什么与边界：** 同时检查路径不触发请求和返回明确预演状态。

<a id="L12"></a>
### 第 12 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L13"></a>
### 第 13 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L14"></a>
### 第 14 行

```python
def test_explicit_opt_in_and_missing_key(monkeypatch):
```

**语法与数据变化：** monkeypatch提供自动恢复环境的测试隔离。

**为什么与边界：** 不依赖开发机是否本来配置了真实Key。

<a id="L15"></a>
### 第 15 行

```python
    monkeypatch.delenv("AGNES_API_KEY", raising=False)
```

**语法与数据变化：** 删除Key，缺失时raising=False不报错。

**为什么与边界：** 用例结束pytest恢复原环境，不将真实Key写入输出。

<a id="L16"></a>
### 第 16 行

```python
    with pytest.raises(ValueError, match="免费"):
```

**语法与数据变化：** 要求缺免费确认时ValueError且文案含免费。

**为什么与边界：** 确保失败原因确实是预算保护，不是后面的缺Key偶然报错。

<a id="L17"></a>
### 第 17 行

```python
        answer("Webhook", live=True)
```

**语法与数据变化：** 只开live，不给免费确认。

**为什么与边界：** 这不能构成调用授权完整条件。

<a id="L18"></a>
### 第 18 行

```python
    with pytest.raises(ValueError, match="AGNES_API_KEY"):
```

**语法与数据变化：** 接着要求缺Key错误中明确配置名称。

**为什么与边界：** 把免费确认与认证配置两个失败原因分开验证。

<a id="L19"></a>
### 第 19 行

```python
        answer("Webhook", live=True, confirmed_current_free=True)
```

**语法与数据变化：** 开live与确认但仍无Key，触发认证前置检查。

**为什么与边界：** 不应发起一个注定失败的HTTP请求再检查配置。

<a id="L20"></a>
### 第 20 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L21"></a>
### 第 21 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L22"></a>
### 第 22 行

```python
def test_one_request_and_no_key_in_result(monkeypatch):
```

**语法与数据变化：** 验证成功mock路径只有一次请求、结果不泄漏Key。

**为什么与边界：** 不是验证供应商实际服务可用。

<a id="L23"></a>
### 第 23 行

```python
    monkeypatch.setenv("AGNES_API_KEY", "test-only-not-a-real-key")
```

**语法与数据变化：** 设置明显无效的测试Key。

**为什么与边界：** MockTransport不连接真实供应商，不要替换成个人真实Key。

<a id="L24"></a>
### 第 24 行

```python
    calls = []
```

**语法与数据变化：** 用列表记录handler收到的请求数。

**为什么与边界：** 外层可读取，避免仅凭客户端配置猜是否重试。

<a id="L25"></a>
### 第 25 行

```python
    def handler(request):
```

**语法与数据变化：** 定义模拟成功响应的处理器。

**为什么与边界：** request来自httpx实际构造的请求对象，可检查URL和JSON体。

<a id="L26"></a>
### 第 26 行

```python
        calls.append(request)
```

**语法与数据变化：** 记录每次请求对象。

**为什么与边界：** 列表长度将直接暴露额外请求。

<a id="L27"></a>
### 第 27 行

```python
        payload = json.loads(request.content)
```

**语法与数据变化：** 把request.content的JSON字节解码为字典。

**为什么与边界：** 可验证发送负载，而不仅是假定构造payload正确。

<a id="L28"></a>
### 第 28 行

```python
        assert str(request.url) == "https://apihub.agnes-ai.com/v1/chat/completions"
```

**语法与数据变化：** 要求精确Agnes聊天完成端点。

**为什么与边界：** 防止端点拼错或悄悄转到另一供应商。

<a id="L29"></a>
### 第 29 行

```python
        assert payload["model"] == "agnes-2.5-flash" and payload["max_tokens"] == 400
```

**语法与数据变化：** 要求指定flash模型且输出上限400。

**为什么与边界：** 这只验证请求字段，不保证供应商价格或实际用量为零。

<a id="L30"></a>
### 第 30 行

```python
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({
```

**语法与数据变化：** 构造HTTP200、choices/message/content结构的模拟响应。

**为什么与边界：** content字段本身又是一段JSON文本，不能把外层API响应和内层答案对象混淆。

<a id="L31"></a>
### 第 31 行

```python
            "answer": "最多重试 3 次，不包含首次投递。", "citation_ids": ["webhook-delivery"], "insufficient_evidence": False})}}]})
```

**语法与数据变化：** 内层fixture含回答、合法引用和False不足标志，再闭合嵌套结构。

**为什么与边界：** 答案是测试作者写的，不是模型能力证据。

<a id="L32"></a>
### 第 32 行

```python
    result = answer("Webhook", live=True, confirmed_current_free=True, transport=httpx.MockTransport(handler))
```

**语法与数据变化：** 显式live/确认并注入mock，执行真实适配器控制流。

**为什么与边界：** live名字不等于真联网：transport决定此测试所有请求被本地拦截。

<a id="L33"></a>
### 第 33 行

```python
    assert len(calls) == 1 and "test-only" not in json.dumps(result)
```

**语法与数据变化：** 要求一次请求，序列化结果中没有测试Key片段。

**为什么与边界：** 不能据此证明所有异常日志都脱敏，后面另外检查错误路径。

<a id="L34"></a>
### 第 34 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L35"></a>
### 第 35 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L36"></a>
### 第 36 行

```python
@pytest.mark.parametrize("status", [302, 401, 402, 429, 500])
```

**语法与数据变化：** 为302、401、402、429、500分别运行错误用例。

**为什么与边界：** 覆盖重定向、认证、权益、限流和服务端失败，不能统称检索无命中。

<a id="L37"></a>
### 第 37 行

```python
def test_errors_no_retry_or_fallback(monkeypatch, status):
```

**语法与数据变化：** 接收当前status与环境fixture。

**为什么与边界：** 每种HTTP失败独立计数。

<a id="L38"></a>
### 第 38 行

```python
    monkeypatch.setenv("AGNES_API_KEY", "test-only")
```

**语法与数据变化：** 设置假Key，满足适配器前置条件。

**为什么与边界：** 不验证真实账号认证。

<a id="L39"></a>
### 第 39 行

```python
    calls = []
```

**语法与数据变化：** 每个用例新建calls，防止其他status污染计数。

**为什么与边界：** 要测的是当前一次调用是否重试。

<a id="L40"></a>
### 第 40 行

```python
    def handler(request):
```

**语法与数据变化：** 定义本状态专用handler。

**为什么与边界：** 闭包读取当前status。

<a id="L41"></a>
### 第 41 行

```python
        calls.append(request)
```

**语法与数据变化：** 记录收到的请求。

**为什么与边界：** 若自动跟随重定向或重试，会多次进入handler。

<a id="L42"></a>
### 第 42 行

```python
        return httpx.Response(status, headers={"Location": "https://example.com"}, text="sensitive error not logged")
```

**语法与数据变化：** 返回当前状态，附重定向地址和敏感错误文本。

**为什么与边界：** 这些是有意设置的负例，错误体不能原样泄漏到面向用户异常。

<a id="L43"></a>
### 第 43 行

```python
    with pytest.raises(RuntimeError, match=f"HTTP {status}") as caught:
```

**语法与数据变化：** 要求RuntimeError含对应HTTP状态，并捕获异常对象。

**为什么与边界：** 避免把其他错误误当本用例成功。

<a id="L44"></a>
### 第 44 行

```python
        answer("Webhook", live=True, confirmed_current_free=True, transport=httpx.MockTransport(handler))
```

**语法与数据变化：** 执行带mock的live路径触发失败。

**为什么与边界：** 不因错误自动退到付费模型或其他端点。

<a id="L45"></a>
### 第 45 行

```python
    assert len(calls) == 1 and "sensitive" not in str(caught.value)
```

**语法与数据变化：** 要求仅一次请求，且异常文本不含sensitive。

**为什么与边界：** 同时覆盖预算保护和错误体最小披露，不检查供应商真实响应。

<a id="L46"></a>
### 第 46 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L47"></a>
### 第 47 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L48"></a>
### 第 48 行

```python
@pytest.mark.parametrize("value", [
```

**语法与数据变化：** 开始参数化四种非法答案对象。

**为什么与边界：** 每项将在下面被序列化为模型返回文本。

<a id="L49"></a>
### 第 49 行

```python
    {"answer": "x", "citation_ids": ["missing"], "insufficient_evidence": False},
```

**语法与数据变化：** 引用missing不在允许集合中。

**为什么与边界：** 用于发现模型捏造来源ID未被拒绝的漏洞。

<a id="L50"></a>
### 第 50 行

```python
    {"answer": "x", "citation_ids": [], "insufficient_evidence": False},
```

**语法与数据变化：** 声称可回答却没有引用。

**为什么与边界：** 格式上是JSON，但不满足本产品的依据契约。

<a id="L51"></a>
### 第 51 行

```python
    {"answer": "x", "citation_ids": ["webhook-delivery"], "insufficient_evidence": True},
```

**语法与数据变化：** 声称证据不足却仍带引用。

**为什么与边界：** 违反本示例拒答应空引用的约定。

<a id="L52"></a>
### 第 52 行

```python
    {"answer": "x", "citation_ids": [], "insufficient_evidence": "true"},
```

**语法与数据变化：** insufficient_evidence使用字符串而非布尔。

**为什么与边界：** 非空字符串truthy不能替代精确布尔校验。

<a id="L53"></a>
### 第 53 行

```python
])
```

**语法与数据变化：** 闭合用例列表及装饰器。

**为什么与边界：** 四项是四次独立测试，不是把四答案一起传函数。

<a id="L54"></a>
### 第 54 行

```python
def test_invalid_output(value):
```

**语法与数据变化：** 接收当前非法value。

**为什么与边界：** 被测函数是输出校验器，不需要模型或HTTP客户端。

<a id="L55"></a>
### 第 55 行

```python
    with pytest.raises(ValueError):
```

**语法与数据变化：** 每项都必须抛ValueError。

**为什么与边界：** 不抛异常就说明非法输出被接纳。

<a id="L56"></a>
### 第 56 行

```python
        validate_answer(json.dumps(value), {"webhook-delivery"})
```

**语法与数据变化：** 转JSON字符串后传白名单仅含Webhook的校验器。

**为什么与边界：** 测试真实解析入口而非绕过json.loads直接传内部对象。

<a id="L57"></a>
### 第 57 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L58"></a>
### 第 58 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L59"></a>
### 第 59 行

```python
def test_no_matching_evidence_skips_model(monkeypatch):
```

**语法与数据变化：** 无候选时即使允许live也应不调用模型。

**为什么与边界：** 这是当前词法候选为空的分支，不等同所有无答案问题都能识别。

<a id="L60"></a>
### 第 60 行

```python
    monkeypatch.setenv("AGNES_API_KEY", "test-only")
```

**语法与数据变化：** 配置假Key避免缺配置先行失败。

**为什么与边界：** 让断言聚焦空证据的短路行为。

<a id="L61"></a>
### 第 61 行

```python
    def forbidden(request):
```

**语法与数据变化：** 定义禁止调用handler。

**为什么与边界：** 若实现仍发出请求，测试立即失败。

<a id="L62"></a>
### 第 62 行

```python
        raise AssertionError("should not call for empty candidates")
```

**语法与数据变化：** 抛AssertionError说明空候选不得调用。

**为什么与边界：** 不是模拟供应商网络错误，而是测试护栏。

<a id="L63"></a>
### 第 63 行

```python
    assert answer("年付折扣是多少？", live=True, confirmed_current_free=True,
```

**语法与数据变化：** 以没有匹配词的折扣问题调用，开启live/确认。

**为什么与边界：** 这不是q09：q09含Webhook会有候选，不能从此用例推出它已解决。

<a id="L64"></a>
### 第 64 行

```python
                  transport=httpx.MockTransport(forbidden))["mode"] == "no model call"
```

**语法与数据变化：** 注入禁止transport，要求mode精确为no model call。

**为什么与边界：** 状态和没有请求两者共同证明当前分支。

<a id="L65"></a>
### 第 65 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L66"></a>
### 第 66 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L67"></a>
### 第 67 行

```python
def test_input_limit():
```

**语法与数据变化：** 定义问题长度与空白输入检查。

**为什么与边界：** 调用prepare即可验证，不需Key。

<a id="L68"></a>
### 第 68 行

```python
    for question in ("", " " * 5, "a" * 1001):
```

**语法与数据变化：** 分别遍历空字符串、全空格、1001字符。

**为什么与边界：** strip后空与超长属于不同失败条件。

<a id="L69"></a>
### 第 69 行

```python
        with pytest.raises(ValueError):
```

**语法与数据变化：** 每种输入都要求ValueError。

**为什么与边界：** 如果循环内某一项被放行，该项即失败。

<a id="L70"></a>
### 第 70 行

```python
            prepare(question)
```

**语法与数据变化：** 实际执行prepare触发输入检查。

**为什么与边界：** 没有任何模型调用，不能把输入错误归为API不可用。

## 跟一遍数据与验证边界

把适配器改为自动重试，应让calls计数断言失败；把拒答布尔改成字符串true，应被validate_answer拒绝。

## 只练一个关键点（不是新的学习验收记录）

1. 运行本文件，找到forbidden与handler各自何时被调用。
2. 在纸面把某一响应改成401，跟踪异常和calls计数预期；无需请求真实端点。
3. **复盘：** mock通过能够证明什么，不能证明什么？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
