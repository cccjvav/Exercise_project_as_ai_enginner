#: 4B 的真实模型对照扩展：需要下载本地模型、配置在线查询改写模型；未默认运行。
import os
from pathlib import Path
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer, CrossEncoder
from langchain_openai import ChatOpenAI
from evidencedesk.documents import load_documents
from evidencedesk.hybrid import rrf

#: 改写数量受限，包含原查询作保底；结构化格式不保证改写保持原意。
class Queries(BaseModel):
    queries: list[str] = Field(min_length=1, max_length=2)

#: 显式模型名和 revision 使模型选择可追溯；下载前检查许可证、内存与网络费用。
def main():
    question = os.environ.get("QUESTION", "Webhook 失败后还会再发吗？")
    docs = load_documents(Path("data/sample"))
    embedding = SentenceTransformer(os.environ["LOCAL_EMBEDDING_MODEL"], revision=os.environ["LOCAL_EMBEDDING_REVISION"])
    reranker = CrossEncoder(os.environ["RERANK_MODEL"], revision=os.environ["RERANK_REVISION"])
    vectors = embedding.encode([doc.title + "\n" + doc.text for doc in docs], normalize_embeddings=True)
    model = ChatOpenAI(model=os.environ["CHAT_MODEL"], temperature=0, max_tokens=200, timeout=30, max_retries=1)
    rewrites = model.with_structured_output(Queries).invoke([
        ("system", "给出至多两条保留原意的检索问题，不增加原问题未提供的事实。"), ("human", question)])
    queries = list(dict.fromkeys([question] + rewrites.queries))
    #: 归一化向量点积等于余弦；前缀按具体模型卡配置，不能任意换。
    rankings = []
    for query in queries:
        vector = embedding.encode(os.environ.get("QUERY_PREFIX", "") + query, normalize_embeddings=True)
        scores = vectors @ vector
        ranking = sorted(range(len(docs)), key=lambda i: (-float(scores[i]), docs[i].id))[:3]
        rankings.append([docs[i].id for i in ranking])
    fused = [doc_id for doc_id, score in rrf(rankings)]
    by_id = {doc.id: doc for doc in docs}
    #: 先召回候选，再联合编码原始问题与每份候选正文；模型应输出每对单一相关性分数。
    scores = reranker.predict([(question, by_id[doc_id].text) for doc_id in fused])
    reranked = sorted(zip(fused, map(float, scores)), key=lambda item: (-item[1], item[0]))
    print({"queries_for_human_review": queries, "vector_rankings": rankings, "rrf": fused, "reranked": reranked})

if __name__ == "__main__":
    main()
