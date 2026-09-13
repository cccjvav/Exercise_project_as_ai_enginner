#: 用包中可靠加载器替代第一课脚本的临时字段提取。
from pathlib import Path
from evidencedesk.documents import load_documents

#: 一行展示身份、标题与正文长度，不在终端重复打印所有手册。
def main():
    for doc in load_documents(Path("data/sample")):
        print(doc.id, doc.title, len(doc.text))

if __name__ == "__main__":
    main()
