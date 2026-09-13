"""Local Linux-x64 lab only. No network listener, no cloud account, no passwords."""
import argparse
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "tools/postgres-runtime/node_modules/@embedded-postgres/linux-x64"
NATIVE = PACKAGE / "native"
DATA = ROOT / "artifacts/postgres/data"
SOCKET = ROOT / "artifacts/postgres/socket"
PORT = 55432


def runtime():
    if not (NATIVE / "bin/postgres").is_file():
        raise SystemExit("先运行 npm --prefix tools/postgres-runtime ci --ignore-scripts")
    # Hydrate only validated links within this package; do not execute npm lifecycle scripts.
    for item in json.loads((NATIVE / "pg-symlinks.json").read_text()):
        source, target = PACKAGE / item["source"], PACKAGE / item["target"]
        if not source.resolve().is_relative_to(NATIVE.resolve()) or not target.parent.resolve().is_relative_to(NATIVE.resolve()):
            raise ValueError("Unexpected symlink outside package")
        if not target.exists():
            target.symlink_to(os.path.relpath(source, target.parent))
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = str(NATIVE / "lib")
    return env


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["init", "serve", "version"])
    args = parser.parse_args()
    env = runtime()
    if args.action == "version":
        subprocess.run([str(NATIVE / "bin/postgres"), "--version"], env=env, check=True)
        return
    SOCKET.mkdir(parents=True, exist_ok=True, mode=0o700)
    SOCKET.chmod(0o700)
    if args.action == "init":
        if (DATA / "PG_VERSION").exists():
            print("已有实验数据库，保留数据，不重复初始化。")
            return
        subprocess.run([str(NATIVE / "bin/initdb"), "-D", str(DATA), "--auth-local=peer",
                        "--auth-host=reject", "--encoding=UTF8", "--locale=C"], env=env, check=True)
        return
    if not (DATA / "PG_VERSION").exists():
        raise SystemExit("请先运行 init")
    # Database access is via an owner-only Unix socket. There is deliberately no TCP port.
    os.execve(str(NATIVE / "bin/postgres"), [str(NATIVE / "bin/postgres"), "-D", str(DATA),
              "-k", str(SOCKET), "-p", str(PORT), "-c", "listen_addresses=", "-c", "shared_buffers=32MB",
              "-c", "max_connections=10"], env)


if __name__ == "__main__":
    main()
