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
