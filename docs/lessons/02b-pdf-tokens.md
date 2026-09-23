# 2B · PDF、文本层与 token

> **1A细度源码精讲（2026-09-19补充）：** [examples/make_demo_pdf.py](../code/examples--make_demo_pdf_py.md) · [examples/pdf_tokens.py](../code/examples--pdf_tokens_py.md) · [tests/test_integrations.py](../code/tests--test_integrations_py.md)。逐行页补充下文的概括表；本课任务和历史问答不变。

[全部课程](../course/index.md) · [上一课](02a-chunks-versions.md) · [下一课](02c-corpus-holdout.md)

- **前置理解：** 2A；安装 ingest extra
- **验证状态：** PDF 样例提取与空页失败已测；token 编码表下载在本环境遇到 TLS 错误，完整计数未验证。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

## 1. 问题：现在为什么需要它？

PDF 看起来有文字，不代表提取器能读到文本；按字符切得下，也不保证模型上下文能放下。我们先拆开文件解析与 token 预算。

## 2. 原理：在这个问题里理解技术

PyPDF 读取文本层，不对扫描图做 OCR。extract_text 可能空或顺序错乱，必须逐页保留页码并抽样检查表格。必要时才评估 Unstructured/OCR，不在空结果时盲目入库。

BPE 类 tokenizer 将字符串映射为 token ID。cl100k_base 只是本课选的一种编码，不代表所有模型；真实上线按所选模型核对编码并预留输出预算。首次 get_encoding 可能下载缓存，所以“本地调用”不等于“首次无需网络”。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `examples/make_demo_pdf.py`

完整源文件：[打开源码](../../examples/make_demo_pdf.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/make_demo_pdf.py -->
```python
#: 只生成虚构英文样例，避免额外字体依赖；生成物放在被 Git 忽略的 artifacts。
from pathlib import Path
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject

#: PDF 文本需要字体资源和内容流；这是最小测试夹具，不是通用排版工具。
def main():
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=200)
    font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"), NameObject("/BaseFont"): NameObject("/Helvetica")})
    page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 30 150 Td (Webhook retries: 3.) Tj ET")
    page[NameObject("/Contents")] = stream
    target = Path("artifacts/demo.pdf")
    target.parent.mkdir(exist_ok=True)
    with target.open("wb") as handle:
        writer.write(handle)
    print(target)

if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–5 | 只生成虚构英文样例，避免额外字体依赖；生成物放在被 Git 忽略的 artifacts。 |
| 6–22 | PDF 文本需要字体资源和内容流；这是最小测试夹具，不是通用排版工具。 |

### `examples/pdf_tokens.py`

完整源文件：[打开源码](../../examples/pdf_tokens.py)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: examples/pdf_tokens.py -->
```python
#: PyPDF 提取文本层，tiktoken 计算某一种编码的 token；两者不负责 OCR。
import argparse
from pypdf import PdfReader
import tiktoken

#: PDF 必须是你有权使用的文件；本脚本只打印长度，避免无意输出原文。
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    args = parser.parse_args()
    reader = PdfReader(args.pdf)
    if reader.is_encrypted:
        raise ValueError("请先通过有授权的流程解密")
    #: 页码从 1 开始；空提取结果是待处理问题，不能静默当成无内容。
    for page_number, page in enumerate(reader.pages, 1):
        text = (page.extract_text() or "").strip()
        if not text:
            raise ValueError(f"第 {page_number} 页无文本层，可能需要 OCR")
        #: 首次加载编码表可能下载缓存；网络失败不应通过关闭 TLS 校验来绕过。
        encoding = tiktoken.get_encoding("cl100k_base")
        token_ids = encoding.encode(text, disallowed_special=())
        print({"page": page_number, "characters": len(text), "tokens": len(token_ids)})

if __name__ == "__main__":
    main()
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–5 | PyPDF 提取文本层，tiktoken 计算某一种编码的 token；两者不负责 OCR。 |
| 6–13 | PDF 必须是你有权使用的文件；本脚本只打印长度，避免无意输出原文。 |
| 14–18 | 页码从 1 开始；空提取结果是待处理问题，不能静默当成无内容。 |
| 19–25 | 首次加载编码表可能下载缓存；网络失败不应通过关闭 TLS 校验来绕过。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
python -m pip install -e ".[ingest]"
python -m examples.make_demo_pdf
python -m examples.pdf_tokens artifacts/demo.pdf
```

### 只做这些关键改动

1. 生成虚构英文 PDF，不上传私人文档。
2. 运行计数，若编码表能下载，预期打印 page=1、characters 与 tokens；不要假设二者相等。
3. 打开 make_demo_pdf，将文案改长，再生成、计数并观察。
4. 若报网络/TLS 错误，先记录下载地址、代理和证书配置；不要关闭证书验证。可先完成 PyPDF 提取测试，token 实验标待验。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

能区分 FileNotFoundError、无文本层与 tokenizer 下载失败。对真实授权 PDF 抽样核对页码和阅读顺序；截图上的字不一定有文本层。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 模型输入预算除了文档块，还包含哪些内容？为什么给全部空间塞满检索结果会导致失败？

**产出：** 可生成的 PDF 夹具、逐页提取/计数脚本、明确的网络前提与错误记录。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。



## 卡住时按需查阅

- https://pypdf.readthedocs.io/en/stable/user/extract-text.html
- https://github.com/openai/tiktoken

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。
