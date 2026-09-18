# Agnes 的安全CLI包装：逐行精讲

[精讲总目录](index.md) · [对应源码](../../examples/agnes_rag.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

将默认dry-run与显式live开关暴露为命令行选项，并把常见契约错误转成非零退出。

### 输入、输出与调用关系

参数传给evidencedesk.agnes.answer，成功输出JSON；常见错误写stderr并退出1。

### 运行与风险边界

`python -m examples.agnes_rag`仅预演。实际live须先核对当前免费权益与外发同意，不能默认启用。

需要本环境安装httpx。不要在聊天/Git中写Key；dry-run没有模型质量证据，live也不保证无幻觉。

## 完整源码

<!-- source: examples/agnes_rag.py -->
```python
"""默认 dry-run 不发送数据；真实调用须由使用者确认免费权益并安全配置环境。"""
import argparse
import json
from evidencedesk.agnes import answer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", default="Webhook 重试多少次？")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--confirmed-current-free", action="store_true")
    args = parser.parse_args()
    try:
        result = answer(args.question, live=args.live, confirmed_current_free=args.confirmed_current_free)
    except (ValueError, RuntimeError) as exc:
        parser.exit(1, str(exc) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
"""默认 dry-run 不发送数据；真实调用须由使用者确认免费权益并安全配置环境。"""
```

**语法与数据变化：** 模块说明强调默认不外发以及显式确认要求。

**为什么与边界：** 只是说明文字，真正开关由argparse和answer的分支共同执行。

<a id="L2"></a>
### 第 2 行

```python
import argparse
```

**语法与数据变化：** 导入 `argparse` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库命令行解析器。它把终端字符串按参数规则转换，type=int 是实际调用整数转换，而不是类型注解。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L3"></a>
### 第 3 行

```python
import json
```

**语法与数据变化：** 导入 `json` 模块；后续通过模块名访问接口。加载模块不等于已经完成下面的业务操作。

**为什么与边界：** 标准库 JSON 编解码器。loads/读入负责解析，dumps 负责生成字符串；JSON 的 true/null 与 Python 的 True/None 对应，序列化不验证事实。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L4"></a>
### 第 4 行

```python
from evidencedesk.agnes import answer
```

**语法与数据变化：** 从 `evidencedesk.agnes` 导入 `answer`，把这些名称绑定到本模块；后面可直接使用，不必重复模块前缀。

**为什么与边界：** prepare准备公开证据与请求，validate_answer检查JSON/引用契约，answer默认dry-run；live仍需显式免费权益确认及配置。 若模块不存在，应检查当前解释器及本课依赖，不要先改业务逻辑掩盖环境问题。

<a id="L5"></a>
### 第 5 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L6"></a>
### 第 6 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L7"></a>
### 第 7 行

```python
def main():
```

**语法与数据变化：** 定义无参入口函数 main，本行创建函数对象，缩进体在调用时才执行；`-> None`（若写出）是返回类型提示。

**为什么与边界：** 将命令解析与业务调用集中到入口，便于测试单独导入其他函数；入口仍需正确处理下面的文件、参数和外部调用错误。

<a id="L8"></a>
### 第 8 行

```python
    parser = argparse.ArgumentParser()
```

**语法与数据变化：** 创建解析器，准备注册三类参数。

**为什么与边界：** 不会自动读取Key或发送请求。

<a id="L9"></a>
### 第 9 行

```python
    parser.add_argument("--question", default="Webhook 重试多少次？")
```

**语法与数据变化：** 问题可选，默认Webhook重试次数。

**为什么与边界：** 默认语料是虚构手册，不能因此把用户私人资料自动加入请求。

<a id="L10"></a>
### 第 10 行

```python
    parser.add_argument("--live", action="store_true")
```

**语法与数据变化：** store_true开关在出现--live时设True，缺省False。

**为什么与边界：** 这是安全默认：仅运行脚本不自动开始模型调用。

<a id="L11"></a>
### 第 11 行

```python
    parser.add_argument("--confirmed-current-free", action="store_true")
```

**语法与数据变化：** 第二个独立开关记录当前免费权益已经人工确认。

**为什么与边界：** 它不是价格API查询，也不能保证未来免费；每次真实调用前仍需核对。

<a id="L12"></a>
### 第 12 行

```python
    args = parser.parse_args()
```

**语法与数据变化：** 解析终端参数，将带连字符的选项映射为下划线属性。

**为什么与边界：** 所以代码使用args.confirmed_current_free，而不是带连字符的Python属性名。

<a id="L13"></a>
### 第 13 行

```python
    try:
```

**语法与数据变化：** 进入可预期错误的处理范围。

**为什么与边界：** 不要用过宽except静默吞掉编程错误。

<a id="L14"></a>
### 第 14 行

```python
        result = answer(args.question, live=args.live, confirmed_current_free=args.confirmed_current_free)
```

**语法与数据变化：** 将问题与两个开关传给真实适配器。

**为什么与边界：** 这里可能只做预演，也可能到达网络路径，取决于显式开关与适配器内部检查。

<a id="L15"></a>
### 第 15 行

```python
    except (ValueError, RuntimeError) as exc:
```

**语法与数据变化：** 捕获适配器的输入/契约错误和运行错误。

**为什么与边界：** 未列出的文件类错误等可能继续向上传播，本脚本不是所有异常的统一包装。

<a id="L16"></a>
### 第 16 行

```python
        parser.exit(1, str(exc) + "\n")
```

**语法与数据变化：** parser.exit以状态1退出并写错误说明。

**为什么与边界：** 不同于parser.error固定usage+状态2；两者都不能当作成功JSON结果。

<a id="L17"></a>
### 第 17 行

```python
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

**语法与数据变化：** 成功时将结果字典编码为保留中文的格式化JSON。

**为什么与边界：** 输出mode可辨dry-run/live；JSON格式正确仍不是答案事实核验。

<a id="L18"></a>
### 第 18 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L19"></a>
### 第 19 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L20"></a>
### 第 20 行

```python
if __name__ == "__main__":
```

**语法与数据变化：** `__name__` 在直接运行脚本/模块入口时是 `__main__`，导入时通常是模块名；条件决定是否进入下一行。

**为什么与边界：** 这样导入函数供测试使用时，不会自动执行此入口。注意其他顶层语句仍会在导入时执行，不能把整个文件视为绝对无副作用。

<a id="L21"></a>
### 第 21 行

```python
    main()
```

**语法与数据变化：** 调用上面定义的入口函数，开始执行其中的操作，不是仅取得函数对象。

**为什么与边界：** 本行通常位于入口保护条件下；可见输出、退出码与副作用由 main 的具体分支决定，异常若未被捕获会向上传播。

## 跟一遍数据与验证边界

没有--live时得到计划，不联网；--live但未确认权益会退出1。网络及输出验证细节见agnes模块精讲。

## 只练一个关键点（不是新的学习验收记录）

1. 运行默认命令，查看mode/model/candidate_ids。
2. 再查看 --help 和 tests/test_agnes.py 的缺确认/缺Key测试；不用真实凭据试错。
3. **复盘：** 命令行成功JSON与stderr非零退出分别代表什么？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
