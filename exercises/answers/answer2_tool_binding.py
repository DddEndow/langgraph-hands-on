"""
===========================================
解答2: 割り算ツール（Chapter 3復習）
===========================================
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from common.llm import llm


# ========== State定義 ==========
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ========== ツール定義 ==========
# 解答1: @tool デコレータ
@tool
def divide(a: int, b: int) -> str:
    """2つの整数を割り算します。"""
    if b == 0:
        return "エラー: 0で割ることはできません"
    result = a / b
    return f"{a} ÷ {b} = {result}"


# ========== ツールリスト ==========
# 解答2: divideをリストに入れる
tools = [divide]


# ========== LLMにツールをバインド ==========
# 解答3: bind_tools でツールをバインド
llm_with_tools = llm.bind_tools(tools)


# ========== ノード関数 ==========
def chatbot(state: State):
    """ツール付きLLMを呼び出すノード"""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def should_continue(state: State):
    """ツール呼び出しが必要かどうか判定する"""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


# ========== グラフ構築 ==========
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)

# 解答4: ToolNodeを作成して追加
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", should_continue, ["tools", END])
builder.add_edge("tools", "chatbot")

graph = builder.compile()


# ========== 実行テスト ==========
if __name__ == "__main__":
    print("=== 割り算ツール ===\n")

    test_inputs = [
        "100を4で割ってください",
        "999÷3は？",
        "50割る0は？",
    ]

    for text in test_inputs:
        print(f"質問: {text}")
        result = graph.invoke({"messages": [("user", text)]})
        print(f"回答: {result['messages'][-1].content}")
        print("-" * 40)
