#: 使用真实 Qdrant 本地内存模式，但向量是手写的，仅解释几何和过滤。
from qdrant_client import QdrantClient, models

#: collection 规定维数与距离函数，查询向量必须同维，真实模型还必须同版本。
def main():
    client = QdrantClient(":memory:")
    client.create_collection("geometry", vectors_config=models.VectorParams(size=2, distance=models.Distance.COSINE))
    client.upsert("geometry", points=[
        models.PointStruct(id=1, vector=[1.0, 0.0], payload={"topic": "重试", "tenant": "alpha"}),
        models.PointStruct(id=2, vector=[0.0, 1.0], payload={"topic": "密钥", "tenant": "alpha"}),
        models.PointStruct(id=3, vector=[0.9, 0.1], payload={"topic": "私有", "tenant": "beta"}),
    ])
    #: 过滤发生在检索候选阶段；第三点再相似，也不能跨租户进入结果。
    scope = models.Filter(must=[models.FieldCondition(key="tenant", match=models.MatchValue(value="alpha"))])
    points = client.query_points("geometry", query=[0.9, 0.1], query_filter=scope, limit=2).points
    print([(point.id, round(point.score, 4)) for point in points])
    assert points[0].id == 1 and all(point.payload["tenant"] == "alpha" for point in points)
    client.close()

if __name__ == "__main__":
    main()
