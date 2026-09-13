from tools.export_space import space_files


def test_bundle_has_no_private_inputs():
    files = space_files()
    assert "Dockerfile" in files and "app_port: 8000" in files["README.md"].decode()
    assert "--uid 1000" in files["Dockerfile"].decode()
    assert "localhost" not in files["frontend/client.ts"].decode().split('fetch(')[-1]
    for name in files:
        assert not name.startswith((".env", ".git/", "artifacts/", "data/raw/", "data/processed/"))
        assert "node_modules" not in name and "AGNES_API_KEY=" not in files[name].decode(errors="ignore")
    assert "src/evidencedesk/api.py" in files and "data/sample/webhook-delivery.md" in files
