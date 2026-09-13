#: Path 表达路径，dataclass 为字段生成初始化方法；此时不需要数据库或框架。
from pathlib import Path
from dataclasses import dataclass

#: frozen 防止误改字段；ID 标识文档，source 定位来源，二者用途不同。
@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str
    source: str

#: 入口先区分不存在与不是目录；这些是输入错误，不应伪装成零命中。
def load_documents(data_dir: Path) -> list[Document]:
    if not data_dir.exists():
        raise FileNotFoundError(data_dir)
    if not data_dir.is_dir():
        raise NotADirectoryError(data_dir)
    documents = []
    #: 只读第一层 Markdown 文件；排序让结果可复现，跳过名字以 .md 结尾的目录。
    for path in sorted(data_dir.glob("*.md")):
        if not path.is_file():
            continue
        source = path.relative_to(data_dir).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()
        #: 先判空再访问首行；startswith 真正校验前缀，而 removeprefix 本身不会报错。
        if not lines or not lines[0].startswith("# "):
            raise ValueError(f"{source}: 第一行必须是 # 标题")
        title = lines[0][2:].strip()
        text = "\n".join(lines[1:]).strip()
        if not title or not text:
            raise ValueError(f"{source}: 标题和正文不能为空")
        #: 每个文件变成一个结构化对象；空目录自然返回空列表。
        documents.append(Document(path.stem, title, text, source))
    return documents
