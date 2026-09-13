#: 前端构建阶段只用于编译；最终镜像不携带 node_modules。
FROM node:22-bookworm-slim AS frontend
WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci --ignore-scripts
COPY frontend/ ./
RUN npm run build

#: 复制明确的课程运行文件，不把 .env、Git 或原始数据打包进去。
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml requirements-tested.lock.txt ./
COPY src/ ./src/
COPY data/sample/ ./data/sample/
COPY --from=frontend /web/index.html /web/client.js ./frontend/
RUN pip install --no-cache-dir -r requirements-tested.lock.txt && pip install --no-deps -e .
#: 非 root 运行；对外绑定 0.0.0.0，浏览器请求仍使用同源相对路径。
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"
CMD ["uvicorn", "evidencedesk.api:app", "--host", "0.0.0.0", "--port", "8000"]
