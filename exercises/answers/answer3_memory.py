"""
===========================================
解答3: 名前を覚えるチャットボット（Chapter 4復習）
===========================================
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# 解答1: MemorySaverをインポート
from langgraph.checkpoint.memory import MemorySaver

from common.llm import llm


# ========== State定義 ==========
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ========== ノード関数 ==========
def chatbot(state: State):
    """LLMを呼び出すノード"""
    return {"messages": [llm.invoke(state["messages"])]}


# ========== グラフ構築 ==========
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)


# ========== メモリセーバーの設定 ==========
# 解答2: MemorySaverを初期化
memory = MemorySaver()

# 解答3: checkpointer引数にmemoryを渡してコンパイル
graph = builder.compile(checkpointer=memory)


# ========== 実行テスト ==========
if __name__ == "__main__":
    print("=== 名前を覚えるチャットボット ===\n")

    # 解答4: thread_idを設定
    config = {"configurable": {"thread_id": "user-session-1"}}

    # 1回目の会話: 名前を伝える
    print("【1回目の会話】")
    input1 = {"messages": [("user", "私の名前は田中太郎です。よろしくお願いします。")]}
    result1 = graph.invoke(input1, config=config)
    print(f"ユーザー: {input1['messages'][0][1]}")
    print(f"アシスタント: {result1['messages'][-1].content}")
    print()

    # 2回目の会話: 名前を覚えているか確認
    print("【2回目の会話】")
    input2 = {"messages": [("user", "私の名前を覚えていますか？")]}
    result2 = graph.invoke(input2, config=config)
    print(f"ユーザー: {input2['messages'][0][1]}")
    print(f"アシスタント: {result2['messages'][-1].content}")
    print()

    # 3回目の会話: 別の話題
    print("【3回目の会話】")
    input3 = {"messages": [("user", "今日は天気が良いですね。")]}
    result3 = graph.invoke(input3, config=config)
    print(f"ユーザー: {input3['messages'][0][1]}")
    print(f"アシスタント: {result3['messages'][-1].content}")
