#: 使用真实 LangGraph，无模型调用；内存 checkpoint 不支持进程重启恢复。
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

#: 类型定义告诉读者状态字段；它本身不执行权限校验。
class State(TypedDict):
    draft: str
    approved: bool
    status: str

#: interrupt 抛出暂停信号，恢复时当前节点从头重跑；前面不能随便放副作用。
def review(state: State):
    decision = interrupt({"draft": state["draft"], "question": "是否批准该草稿？"})
    return {"approved": decision is True}

#: 只计算状态，不写工单；审批通过和拥有写权限是两个不同条件。
def route(state: State):
    return {"status": "ready_for_authorized_tool" if state["approved"] else "rejected"}

#: 图明确固定执行顺序；这类流程不需要模型自主选择下一步。
def build_graph():
    graph = StateGraph(State)
    graph.add_node("review", review)
    graph.add_node("route", route)
    graph.add_edge(START, "review")
    graph.add_edge("review", "route")
    graph.add_edge("route", END)
    return graph.compile(checkpointer=InMemorySaver())

#: thread_id 必须由可信服务映射到当前用户；仅拼接身份字符串不构成鉴权。
def main():
    graph = build_graph()
    config = {"configurable": {"thread_id": "alpha:alice:demo-1"}}
    paused = graph.invoke({"draft": "Webhook 投递失败排查", "approved": False, "status": "draft"}, config)
    assert "__interrupt__" in paused
    print("已暂停，未执行任何工单写操作")
    resumed = graph.invoke(Command(resume=True), config)
    print(resumed["status"])

if __name__ == "__main__":
    main()
