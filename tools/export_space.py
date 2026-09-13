"""Create a small allowlisted Hugging Face Docker Space bundle, without uploading it."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def space_files() -> dict[str, bytes]:
    selected = [ROOT / path for path in ["pyproject.toml", "requirements-tested.lock.txt",
        "frontend/index.html", "frontend/client.ts", "frontend/package.json", "frontend/package-lock.json", "frontend/tsconfig.json"]]
    selected += sorted((ROOT / "src/evidencedesk").glob("*.py"))
    selected += sorted((ROOT / "data/sample").glob("*.md"))
    files = {path.relative_to(ROOT).as_posix(): path.read_bytes() for path in selected}
    docker = (ROOT / "deploy/Dockerfile").read_text().replace("useradd --create-home appuser", "useradd --create-home --uid 1000 appuser")
    files["Dockerfile"] = docker.encode()
    files["README.md"] = (ROOT / "deploy/huggingface/README.md").read_bytes()
    files[".dockerignore"] = (ROOT / ".dockerignore").read_bytes()
    return files


def main():
    target = ROOT / "artifacts/evidencedesk-space.zip"
    target.parent.mkdir(exist_ok=True)
    files = space_files()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            archive.writestr(name, content)
    print(f"Prepared {len(files)} allowlisted files, {target.stat().st_size} bytes. No upload or cloud resource creation.")
    print("artifacts/evidencedesk-space.zip")


if __name__ == "__main__":
    main()
