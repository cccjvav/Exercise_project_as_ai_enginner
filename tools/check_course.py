"""无网络校验：课程本地链接、完整源码同步、Python 语法、课数。"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    count = 0
    for doc in [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]:
        text = doc.read_text(encoding="utf-8")
        # Links in fenced source examples are not documentation navigation links.
        without_code = re.sub(r"```.*?```", "", text, flags=re.S)
        for link in re.findall(r"\]\(([^)]+)\)", without_code):
            if link.startswith(("https://", "http://", "#", "mailto:")):
                continue
            target = (doc.parent / link.split("#")[0]).resolve()
            assert target.exists(), f"Broken local link: {doc.relative_to(ROOT)} -> {link}"
        for source, code in re.findall(r"<!-- source: (.*?) -->\n```[^\n]*\n(.*?)```", text, re.S):
            assert (ROOT / source).read_text(encoding="utf-8") == code, f"Source drift: {doc.name} / {source}"
            count += 1
    for path in [*(ROOT / "src").rglob("*.py"), *(ROOT / "examples").glob("*.py"), *(ROOT / "tests").glob("*.py")]:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lessons = list((ROOT / "docs/lessons").glob("[0-9][0-9][a-z]-*.md"))
    assert len(lessons) == 22, len(lessons)
    print(f"PASS: 22 lessons; {count} embedded source copies match; local links and Python syntax valid")

if __name__ == "__main__":
    main()
