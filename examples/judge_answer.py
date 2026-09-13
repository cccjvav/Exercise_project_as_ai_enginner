#: 在线可选：Ragas 的 LLM 裁判也会收费，且评分有随机性与模型偏差。
import asyncio
import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from ragas import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness
from evidencedesk.documents import load_documents

#: 从真实候选答案构造单条评测，不能把人工标准答案伪装为系统输出。
async def main():
    os.environ["OPENAI_API_KEY"]
    candidate = os.environ["CANDIDATE_ANSWER"]
    doc = next(doc for doc in load_documents(Path("data/sample")) if doc.id == "webhook-delivery")
    sample = SingleTurnSample(user_input="Webhook 重试多少次？", response=candidate, retrieved_contexts=[doc.text])
    #: 此接口属于 Ragas 0.3 系列；升级应先核对迁移说明，不能只更新版本号。
    judge = LangchainLLMWrapper(ChatOpenAI(model=os.environ["JUDGE_MODEL"], temperature=0, timeout=30, max_retries=1))
    metric = Faithfulness(llm=judge)
    score = await metric.single_turn_ascore(sample)
    print({"metric": "faithfulness", "score": score, "human_review_required": True})

if __name__ == "__main__":
    asyncio.run(main())
