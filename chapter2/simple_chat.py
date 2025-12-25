import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from common.llm import llm

# 1. Stateの定義（メッセージを追記していく形式）
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Nodeの定義（チャットボット機能）
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# 3. Graphの構築
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

# エッジの定義 (Start -> chatbot -> End)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# コンパイル
graph = graph_builder.compile()

# 実行
user_input = "こんにちは！"
# user_input = "こんにちは！東京都で一番有名な会社を教えて"
for event in graph.stream({"messages": [("user", user_input)]}):
    for value in event.values():
        print("Assistant:", value["messages"][-1].content)

# print(graph.get_graph().draw_mermaid())
