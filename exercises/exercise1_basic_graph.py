"""
===========================================
練習問題1: 翻訳チャットボット（Chapter 2復習）
===========================================

【目的】
LangGraphの基本3要素（State, Node, Edge）を使って
シンプルなグラフを構築できることを確認します。

【課題】
ユーザーの入力を英語に翻訳するチャットボットを作成してください。
以下の要件を満たすグラフを構築してください：

ヒント
- "translator"という名前でノードを追加する（translator関数を使用）
- translatorノードからSTARTやENDへのエッジを追加する

【参考】
- chapter2/simple_chat.py を参考にしてください
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

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


# ========== グラフ構築（ここを実装）==========
graph_builder = None
graph = None


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
