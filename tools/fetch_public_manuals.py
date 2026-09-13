"""Fetch a pinned small MIT-licensed documentation sample using gh's authenticated API.
Raw and normalized copies remain in ignored data directories. No third-party code is executed.
"""
import base64
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def github_file(repo: str, revision: str, path: str) -> bytes:
    result = subprocess.run(["gh", "api", f"repos/{repo}/contents/{path}?ref={revision}"],
                            capture_output=True, text=True, check=True)
    record = json.loads(result.stdout)
    if record.get("encoding") != "base64" or record["size"] > 250_000:
        raise ValueError("Only small regular text files are supported")
    content = base64.b64decode(record["content"], validate=False)
    if len(content) != record["size"]:
        raise ValueError("Downloaded size mismatch")
    return content


def main():
    manifest = json.loads((ROOT / "data/sources/fastapi.json").read_text())
    repo, revision = manifest["repository"], manifest["revision"]
    license_bytes = github_file(repo, revision, manifest["license_path"])
    if b"Permission is hereby granted" not in license_bytes:
        raise ValueError("Expected MIT license; review source before use")
    downloaded = [(doc, github_file(repo, revision, doc["path"])) for doc in manifest["documents"]]
    raw_dir = ROOT / "data/raw/fastapi"
    processed = ROOT / "data/processed/fastapi"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)
    for folder in (raw_dir, processed):
        (folder / "LICENSE.txt").write_bytes(license_bytes)
    provenance = []
    for doc, content in downloaded:
        (raw_dir / f"{doc['id']}.md").write_bytes(content)
        url = f"https://github.com/{repo}/blob/{revision}/{doc['path']}"
        text = f"# {doc['title']}\n\nSource: {url}\nLicense: MIT; see LICENSE.txt.\n\n" + content.decode("utf-8")
        (processed / f"{doc['id']}.md").write_text(text, encoding="utf-8")
        provenance.append({**doc, "url": url, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)})
    report = {"repository": repo, "revision": revision, "license": manifest["license"],
              "license_sha256": hashlib.sha256(license_bytes).hexdigest(), "documents": provenance}
    (processed / "provenance.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"downloaded": len(downloaded), "raw_bytes": sum(len(b) for _, b in downloaded),
                      "directory": "data/processed/fastapi", "revision": revision}, indent=2))


if __name__ == "__main__":
    main()
