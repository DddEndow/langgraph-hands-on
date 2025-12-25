import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from common.llm import llm

# 1. Stateの定義（メッセージを追記していく形式）
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. ツールの定義
@tool
def multiply(a: int, b: int) -> int:
    """2つの整数を掛け算します。"""
    return a * b

tools = [multiply]
llm_with_tools = llm.bind_tools(tools) # Geminiにツールを教える

# 3. Nodeの定義
def chatbot_with_tools(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# 4. Graphの構築
builder = StateGraph(State)
builder.add_node("chatbot", chatbot_with_tools)
builder.add_node("tools", ToolNode(tools)) # ツール実行用ノード

builder.add_edge(START, "chatbot")

# 5. 条件付きエッジの定義
def should_continue(state: State):
    messages = state["messages"]
    last_message = messages[-1]
    # ツール呼び出しが含まれていればツールノードへ
    if last_message.tool_calls:
        return "tools"
    return END

builder.add_conditional_edges("chatbot", should_continue, ["tools", END])
builder.add_edge("tools", "chatbot") # ツール実行後はチャットに戻る

agent = builder.compile()

# 実行（計算が必要な問いかけ）
# Geminiは自分でmultiplyツールを選び、実行結果を受け取って回答します
inputs = {"messages": [("user", "123かける456は？")]}
# inputs = {"messages": [("user", "999かける567の結果に3をかけた結果は？")]}
for event in agent.stream(inputs):
    for key, value in event.items():
        print(f"Node '{key}':") 
        print(value)
        print("---")
