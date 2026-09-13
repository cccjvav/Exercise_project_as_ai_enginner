"""Execute real PostgreSQL RLS tests; only the owned local lab socket is used.
Temporary schema/role names are random. Only those resources are cleaned up.
"""
import argparse
import hashlib
import json
from pathlib import Path
from uuid import uuid4
import psycopg
from psycopg import sql
from evidencedesk.documents import load_documents

ROOT = Path(__file__).resolve().parents[1]
SOCKET = ROOT / "artifacts/postgres/socket"


def connect():
    return psycopg.connect(host=str(SOCKET), port=55432, dbname="postgres", autocommit=True)


def persisted():
    with connect() as conn:
        count = conn.execute("SELECT count(*) FROM evidencedesk_lab_state.runs").fetchone()[0]
        assert count > 0
        print(json.dumps({"persisted_run_count": count, "restart_read": "PASS"}))


def run():
    schema = "course_" + uuid4().hex[:16]
    role = "reader_" + uuid4().hex[:16]
    checks = []
    sample = load_documents(ROOT / "data/sample")
    public = load_documents(ROOT / "data/processed/fastapi")
    with connect() as conn:
        version = conn.execute("SELECT version()").fetchone()[0]
        conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        conn.execute(sql.SQL("CREATE ROLE {} NOLOGIN NOSUPERUSER NOBYPASSRLS").format(sql.Identifier(role)))
        try:
            conn.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
            conn.execute((ROOT / "deploy/schema.sql").read_text())
            for tenant, docs in [("alpha", sample), ("beta", public)]:
                for doc in docs:
                    conn.execute("INSERT INTO documents VALUES (%s,%s,%s,%s)",
                                 (tenant, doc.id, hashlib.sha256(doc.text.encode()).hexdigest(), doc.text))
            conn.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(sql.Identifier(schema), sql.Identifier(role)))
            conn.execute(sql.SQL("GRANT SELECT,INSERT,UPDATE ON documents TO {}").format(sql.Identifier(role)))
            for tenant, expected in [("alpha", sample), ("beta", public)]:
                with conn.transaction():
                    conn.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
                    current, superuser, bypass = conn.execute("SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user").fetchone()
                    assert current == role and not superuser and not bypass
                    conn.execute("SELECT set_config('app.tenant_id', %s, true)", (tenant,))
                    actual = conn.execute("SELECT document_id FROM documents").fetchall()
                    assert {row[0] for row in actual} == {doc.id for doc in expected}
                checks.append(f"{tenant}: non-superuser tenant isolation PASS")
            try:
                with conn.transaction():
                    conn.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
                    conn.execute("SELECT set_config('app.tenant_id', 'alpha', true)")
                    conn.execute("INSERT INTO documents VALUES ('beta','forbidden','v1','blocked')")
            except psycopg.errors.InsufficientPrivilege:
                checks.append("cross-tenant INSERT rejected PASS")
            else:
                raise AssertionError("RLS write check failed")
            try:
                with conn.transaction():
                    conn.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
                    conn.execute("SELECT set_config('app.tenant_id', 'alpha', true)")
                    conn.execute("UPDATE documents SET tenant_id='beta' WHERE document_id='webhook-delivery'")
            except psycopg.errors.InsufficientPrivilege:
                checks.append("cross-tenant UPDATE rejected PASS")
            else:
                raise AssertionError("RLS update check failed")
            with conn.transaction():
                conn.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
                setting = conn.execute("SELECT current_setting('app.tenant_id',true)").fetchone()[0]
                assert setting in (None, "")
                assert conn.execute("SELECT count(*) FROM documents").fetchone()[0] == 0
            checks.append("transaction-local identity reset; no identity sees zero rows PASS")
            # Keep only a tiny nonsensitive receipt to verify a server restart, not copied document bodies.
            conn.execute("CREATE SCHEMA IF NOT EXISTS evidencedesk_lab_state")
            conn.execute("CREATE TABLE IF NOT EXISTS evidencedesk_lab_state.runs (id text PRIMARY KEY, checked_at timestamptz DEFAULT now())")
            conn.execute("INSERT INTO evidencedesk_lab_state.runs(id) VALUES(%s)", (uuid4().hex,))
        finally:
            conn.execute("RESET search_path")
            conn.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
            conn.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(role)))
    result = {"postgres": version, "transport": "private Unix socket; TCP disabled", "documents_imported": len(sample)+len(public),
              "synthetic_documents": len(sample), "public_licensed_documents": len(public), "checks": checks,
              "scope": "documents RLS only; app authentication, tickets RLS and managed cloud DB not certified"}
    path = ROOT / "artifacts/postgres-validation.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-persisted", action="store_true")
    args = parser.parse_args()
    persisted() if args.check_persisted else run()
