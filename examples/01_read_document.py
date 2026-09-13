from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "data" / "sample" / "webhook-delivery.md"
raw_text = path.read_text(encoding="utf-8")
lines = raw_text.splitlines()

document_id = path.stem
title = lines[0].removeprefix("# ").strip()
body = "\n".join(lines[1:]).strip()
source = path.relative_to(ROOT / "data" / "sample").as_posix()

print(f"ID: {document_id}")
print(f"标题: {title}")
print(f"来源: {source}")
print("正文:")
print(body)
