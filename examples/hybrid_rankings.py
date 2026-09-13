#: 这是排名机制实验，不是假装已跑完真实向量对照。
from evidencedesk.hybrid import bm25, rrf, expand_parents

#: 显式 token 列表保留词频，和阶段 1 的去重词集合形成对比。
def main():
    corpus = {"retry": ["webhook", "重试", "重试"], "keys": ["密钥", "轮换"], "ticket": ["故障", "工单"]}
    lexical = [doc_id for doc_id, score in bm25(["webhook", "重试"], corpus)]
    vector_fixture = ["keys", "retry"]
    print({"bm25": lexical, "fixture_vector": vector_fixture, "rrf": rrf([lexical, vector_fixture])})
    print(expand_parents(["child-a", "child-b"], {"child-a": "parent-1", "child-b": "parent-1"}))

if __name__ == "__main__":
    main()
