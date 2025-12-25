"""
===========================================
解答1: 翻訳チャットボット（Chapter 2復習）
===========================================
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from common.llm import llm


# ========== State定義 ==========
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ========== ノード関数 ==========
def translator(state: State):
    """ユーザーの入力を英語に翻訳するノード"""
    system_msg = "ユーザーの入力を英語に翻訳してください。翻訳結果のみを出力してください。"
    messages = [("system", system_msg)] + state["messages"]
    return {"messages": [llm.invoke(messages)]}


# ========== グラフ構築 ==========
# 解答1: StateGraphを初期化
graph_builder = StateGraph(State)

# 解答2: "translator"という名前でノードを追加
graph_builder.add_node("translator", translator)

# 解答3: STARTから"translator"へエッジを追加
graph_builder.add_edge(START, "translator")

# 解答4: "translator"からENDへエッジを追加
graph_builder.add_edge("translator", END)

# 解答5: グラフをコンパイル
graph = graph_builder.compile()


# ========== 実行テスト ==========
if __name__ == "__main__":
    print("=== 翻訳チャットボット ===\n")

    test_inputs = [
        "こんにちは、今日は良い天気ですね",
        "私はプログラミングが好きです",
        "明日の会議は何時からですか？",
    ]

    for text in test_inputs:
        print(f"入力: {text}")
        result = graph.invoke({"messages": [("user", text)]})
        print(f"翻訳: {result['messages'][-1].content}")
        print("-" * 40)
