"""
Chapter 3-3: グラフの可視化

学習目標:
- LangGraphのグラフ構造をMermaid記法で出力する方法
- デバッグやドキュメント作成への活用
- 各チャプターのグラフ構造を視覚的に理解
"""
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

# ========================================
# グラフの定義（Chapter 3と同様の構造）
# ========================================

class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def multiply(a: int, b: int) -> int:
    """2つの整数を掛け算します。"""
    return a * b

tools = [multiply]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def should_continue(state: State):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# グラフの構築
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", should_continue, ["tools", END])
builder.add_edge("tools", "chatbot")

graph = builder.compile()

# ========================================
# グラフの可視化
# ========================================

if __name__ == "__main__":
    print("=" * 50)
    print("LangGraph グラフ構造の可視化")
    print("=" * 50)
    print()

    # 方法1: Mermaid記法で出力
    print("【Mermaid記法での出力】")
    print("-" * 30)
    mermaid_code = graph.get_graph().draw_mermaid()
    print(mermaid_code)
    print()

    print("【使い方】")
    print("上記のMermaidコードを以下の場所で可視化できます:")
    print("1. https://mermaid.live/ にペースト")
    print("2. GitHubのMarkdownに ```mermaid ブロックで記載")
    print("3. VSCodeのMermaid拡張機能で表示")
    print()

    # 方法2: ASCIIアートで出力（シンプルな確認用）
    print("【グラフ構造の説明】")
    print("-" * 30)
    print("""
    このグラフの流れ:

    [START]
        │
        ▼
    ┌─────────┐
    │ chatbot │ ◀──────────┐
    └────┬────┘            │
         │                 │
         ▼                 │
    (should_continue)      │
         │                 │
    ┌────┴────┐            │
    │         │            │
    ▼         ▼            │
  [END]   ┌───────┐        │
          │ tools │────────┘
          └───────┘

    ・chatbotノード: LLMを呼び出してメッセージを生成
    ・should_continue: ツール呼び出しが必要か判定
    ・toolsノード: ツールを実行して結果を返す
    ・ループ: ツール実行後、再びchatbotへ
    """)

    # 方法3: ノードとエッジの情報を取得
    print("【グラフの詳細情報】")
    print("-" * 30)
    graph_structure = graph.get_graph()
    print(f"ノード: {list(graph_structure.nodes.keys())}")
    print(f"エッジ数: {len(graph_structure.edges)}")
