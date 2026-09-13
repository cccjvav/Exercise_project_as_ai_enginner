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
