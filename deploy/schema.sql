--: 使用事务避免半套 schema；用于空的实验数据库，生产迁移需专门版本工具。
BEGIN;
CREATE TABLE documents (
    tenant_id text NOT NULL,
    document_id text NOT NULL,
    version text NOT NULL,
    body text NOT NULL,
    PRIMARY KEY (tenant_id, document_id)
);
--: RLS 使行可见性取决于会话身份；应用必须是非超级用户、非 BYPASSRLS 角色。
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON documents
    USING (tenant_id = current_setting('app.tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true));
--: 幂等键以租户为作用域，唯一约束处理并发冲突，而不是仅靠先查询后插入。
CREATE TABLE tickets (
    tenant_id text NOT NULL,
    idempotency_key text NOT NULL,
    approved_payload_hash text NOT NULL,
    ticket_id uuid NOT NULL,
    PRIMARY KEY (tenant_id, idempotency_key)
);
COMMIT;
