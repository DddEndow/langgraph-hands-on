"""
Chapter 5: Human-in-the-loop（人間による承認）

学習目標:
- interrupt_beforeを使った実行の一時停止
- ユーザー承認後に処理を再開する方法
- 重要な操作の前に確認を挟むパターン
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from common.llm import llm

# 1. Stateの定義
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. 機密性の高いツールを定義（実行前に承認が必要）
@tool
def send_email(to: str, subject: str, body: str) -> str:
    """メールを送信します（デモ用ダミー）。"""
    return f"メールを送信しました: 宛先={to}, 件名={subject}"

@tool
def delete_file(filename: str) -> str:
    """ファイルを削除します（デモ用ダミー）。"""
    return f"ファイル '{filename}' を削除しました"

@tool
def get_info(query: str) -> str:
    """情報を検索します（安全なツール）。"""
    return f"'{query}' に関する情報: これはサンプルデータです。"

# 3. ツール設定
tools = [send_email, delete_file, get_info]
llm_with_tools = llm.bind_tools(tools)

# 4. Nodeの定義
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# 5. Graphの構築
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "chatbot")

def should_continue(state: State):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

builder.add_conditional_edges("chatbot", should_continue, ["tools", END])
builder.add_edge("tools", "chatbot")

# 6. Human-in-the-loop: toolsノードの実行前に一時停止
memory = MemorySaver()
agent = builder.compile(
    checkpointer=memory,
    interrupt_before=["tools"]  # toolsノードの前で停止
)

# 7. 実行デモ（ループ対応版）
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "demo-1"}}

    print("=== Human-in-the-loop デモ ===")
    print("終了するには 'exit' または 'quit' と入力してください\n")

    # 初回メッセージを設定
    initial_message = "test@example.comに「会議の件」という件名でメールを送って"
    first_run = True

    while True:
        # 初回は自動入力、2回目以降はユーザー入力
        if first_run:
            user_input = initial_message
            print(f"ユーザー: {user_input}\n")
            first_run = False
        else:
            user_input = input("ユーザー: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("終了します。")
                break

            if not user_input:
                continue

        # グラフを実行
        for event in agent.stream({"messages": [("user", user_input)]}, config):
            for key, value in event.items():
                if key != "__end__":
                    print(f"[{key}] 処理中...")

        # 現在の状態を確認
        state = agent.get_state(config)
        last_message = state.values["messages"][-1]

        # ツール呼び出しがある場合は承認を求める
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            pending_tools = last_message.tool_calls

            print("\n--- 実行が一時停止されました ---")
            print("承認待ちのツール呼び出し:")
            for tc in pending_tools:
                print(f"  - {tc['name']}: {tc['args']}")

            print("\nこの操作を実行しますか？")
            approval = input("y/n: ").strip().lower()

            if approval == "y":
                print("\n--- 承認されました。処理を再開します ---\n")
                for event in agent.stream(None, config):
                    for key, value in event.items():
                        if key != "__end__":
                            print(f"[{key}] 処理中...")

                # 再開後の状態を取得
                final_state = agent.get_state(config)
                print(f"\nアシスタント: {final_state.values['messages'][-1].content}\n")
            else:
                print("\n--- 操作がキャンセルされました ---\n")
        else:
            # ツール呼び出しがない場合は通常の応答を表示
            print(f"\nアシスタント: {last_message.content}\n")
