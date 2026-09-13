"""Refresh source copies and nearby-comment line tables without rewriting lesson prose."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(
    r"(<!-- source: ([^\n]+) -->\n```[^\n]*\n)(.*?)(```\n\n#### 逐行 / 相邻语句讲解\n\n)(\|[^\n]*\n(?:\|[^\n]*\n)*)",
    re.S,
)


def replace(match):
    source = (ROOT / match[2]).read_text(encoding="utf-8")
    lines = source.splitlines()
    markers = []
    for number, line in enumerate(lines, 1):
        comment = re.match(r"\s*(?:#|//|--):\s*(.*)", line)
        if comment:
            markers.append((number, comment[1]))
    table = "| 源码行 | 为什么这样写、数据如何变化 |\n|---|---|\n"
    for index, (start, text) in enumerate(markers):
        end = markers[index + 1][0] - 1 if index + 1 < len(markers) else len(lines)
        table += f"| {start}–{end} | {text.replace('|', '／')} |\n"
    if not markers:
        table += "| 全文件 | 配置字段按小课原理和操作步骤解释；修改后以构建和测试验证。 |\n"
    return match[1] + source + match[4] + table


def main():
    changed = 0
    for path in (ROOT / "docs/lessons").glob("*.md"):
        old = path.read_text(encoding="utf-8")
        new = PATTERN.sub(replace, old)
        if old != new:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"Updated {changed} lesson source copies / line tables")


if __name__ == "__main__":
    main()
