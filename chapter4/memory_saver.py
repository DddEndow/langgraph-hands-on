import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from common.llm import llm

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

builder = StateGraph(State)

builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

agent = builder.compile()

memory = MemorySaver()
# checkpointerを指定してコンパイル
agent_with_memory = builder.compile(checkpointer=memory)

# thread_idを指定して会話
config = {"configurable": {"thread_id": "1"}}

# 1回目の会話
print("--- Round 1 ---")
input1 = {"messages": [("user", "私の名前はGemini太郎です。")]}
result1 = agent_with_memory.invoke(input1, config=config)
print(result1["messages"][-1].content)

# 2回目の会話（前の会話を覚えているか？）
print("--- Round 2 ---")
input2 = {"messages": [("user", "私の名前を覚えていますか？")]}
result2 = agent_with_memory.invoke(input2, config=config)
print(result2["messages"][-1].content)

# 3回目の会話（別の会話）
print("--- Round 3 ---")
config3 = {"configurable": {"thread_id": "3"}}
input3 = {"messages": [("user", "私の名前を覚えていますか？")]}
result3 = agent_with_memory.invoke(input3, config=config3)
print(result3["messages"][-1].content)
