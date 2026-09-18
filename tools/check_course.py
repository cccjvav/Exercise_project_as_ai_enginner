"""无网络校验：课程本地链接、完整源码同步、Python 语法、课数。"""
import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    count = 0
    for doc in [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]:
        text = doc.read_text(encoding="utf-8")
        # Links in fenced source examples are not documentation navigation links.
        without_code = re.sub(r"^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*$", "", text, flags=re.S | re.M)
        for link in re.findall(r"\]\(([^)]+)\)", without_code):
            if link.startswith(("https://", "http://", "#", "mailto:")):
                continue
            target = (doc.parent / link.split("#")[0]).resolve()
            assert target.exists(), f"Broken local link: {doc.relative_to(ROOT)} -> {link}"
        for source, fence, code in re.findall(r"<!-- source: ([^\n]+) -->\n(`{3,}|~{3,})[^\n]*\n(.*?)^\2[ \t]*$", text, re.S | re.M):
            assert (ROOT / source).read_text(encoding="utf-8") == code, f"Source drift: {doc.name} / {source}"
            count += 1
    manifest = json.loads((ROOT / "docs/code/manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"] + manifest["supplementary"]:
        raw = (ROOT / entry["source"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"], f"Guide source changed: {entry['source']}"
        total = len(raw.decode("utf-8").splitlines())
        assert total == entry["line_count"], entry["source"]
        if entry.get("coverage") == "individual-lines":
            page = (ROOT / entry["page"]).read_text(encoding="utf-8")
            expected = list(range(1, total + 1))
            assert entry["explained_lines"] == expected, entry["source"]
            assert re.findall(r'<a id="L(\d+)"></a>', page) == list(map(str, expected)), entry["page"]
    for path in [*(ROOT / "src").rglob("*.py"), *(ROOT / "examples").glob("*.py"), *(ROOT / "tests").glob("*.py")]:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lessons = list((ROOT / "docs/lessons").glob("[0-9][0-9][a-z]-*.md"))
    assert len(lessons) == 22, len(lessons)
    print(f"PASS: 22 lessons; {count} embedded source copies match; local links and Python syntax valid")

if __name__ == "__main__":
    main()
