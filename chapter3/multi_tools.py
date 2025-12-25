"""
Chapter 3-2: 複数ツールを使うエージェント

学習目標:
- 複数のツールを定義してLLMにバインドする方法
- LLMが状況に応じて適切なツールを選択する仕組み
- 実践的なエージェント構築パターン
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from common.llm import llm

# 1. Stateの定義
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. 複数のツールを定義
@tool
def add(a: int, b: int) -> int:
    """2つの整数を足し算します。"""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """2つの整数を掛け算します。"""
    return a * b

@tool
def search_weather(city: str) -> str:
    """指定した都市の天気を検索します（デモ用ダミーデータ）。"""
    # 実際のAPIは使わず、デモ用の固定データを返す
    weather_data = {
        "東京": "晴れ、気温15度",
        "大阪": "曇り、気温13度",
        "福岡": "雨、気温12度",
    }
    return weather_data.get(city, f"{city}の天気情報は見つかりませんでした")

@tool
def get_current_time() -> str:
    """現在の日時を取得します。"""
    from datetime import datetime
    return datetime.now().strftime("%Y年%m月%d日 %H時%M分")

# 3. ツールをリストにまとめてLLMにバインド
tools = [add, multiply, search_weather, get_current_time]
llm_with_tools = llm.bind_tools(tools)

# 4. Nodeの定義
SYSTEM_PROMPT = """あなたは親切なアシスタントです。
以下のツールを使用できます：
- add: 足し算
- multiply: 掛け算
- search_weather: 天気検索
- get_current_time: 現在時刻取得

ツールが必要な質問にはツールを使用してください。
ツールが不要な一般的な質問（例：概念の説明、アドバイスなど）には、あなた自身の知識で回答してください。"""

def chatbot(state: State):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    return {"messages": [llm_with_tools.invoke(messages)]}

# 5. Graphの構築
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "chatbot")

# 6. 条件付きエッジ
def should_continue(state: State):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

builder.add_conditional_edges("chatbot", should_continue, ["tools", END])
builder.add_edge("tools", "chatbot")

agent = builder.compile()

# 7. 実行テスト
if __name__ == "__main__":
    # テスト1: 計算（加算）
    print("=== テスト1: 計算（加算） ===")
    result = agent.invoke({"messages": [("user", "25と75を足すといくつ？")]})
    print(result["messages"][-1].content)
    print()

    # テスト2: 計算（乗算）
    print("=== テスト2: 計算（乗算） ===")
    result = agent.invoke({"messages": [("user", "12かける8は？")]})
    print(result["messages"][-1].content)
    print()

    # テスト3: 天気検索
    print("=== テスト3: 天気検索 ===")
    result = agent.invoke({"messages": [("user", "東京の天気を教えて")]})
    print(result["messages"][-1].content)
    print()

    # テスト4: 現在時刻
    print("=== テスト4: 現在時刻 ===")
    result = agent.invoke({"messages": [("user", "今何時？")]})
    print(result["messages"][-1].content)
    print()

    # テスト5: 複合的な質問（ツールが不要な場合）
    print("=== テスト5: 通常の質問（ツール不要） ===")
    result = agent.invoke({"messages": [("user", "LangGraphとは何ですか？")]})
    print(result["messages"][-1].content)
