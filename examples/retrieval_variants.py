#: MultiQuery 与 rerank 先用受控 fixture 演示数据流，真实质量需要模型和实验验证。
from evidencedesk.hybrid import rrf, expand_parents

#: 两条查询的候选排名来自固定样例，不宣称是模型自动改写的结果。
def main():
    original_ranking = ["retry-child", "keys-child"]
    rewritten_ranking = ["retry-child", "ticket-child"]
    fused = [doc_id for doc_id, score in rrf([original_ranking, rewritten_ranking])]
    #: Cross-encoder 对 (query, passage) 打分；这里用预置分数替身验证排序连接方式。
    fixture_pair_scores = {"retry-child": 0.8, "keys-child": 0.1, "ticket-child": 0.3}
    reranked = sorted(fused, key=lambda item: (-fixture_pair_scores[item], item))[:2]
    parents = expand_parents(reranked, {"retry-child": "webhook-delivery", "keys-child": "api-key-policy", "ticket-child": "incident-escalation"})
    print({"fused": fused, "fixture_reranked": reranked, "parents": parents})

if __name__ == "__main__":
    main()
