import os
from langchain_google_genai import ChatGoogleGenerativeAI

# APIキーの設定（環境変数推奨ですが、ハンズオンでは直接入力も可）
os.environ["GOOGLE_API_KEY"] = "API_KEY"

# モデルの初期化 (高速なFlashモデルを推奨)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# テスト実行
response = llm.invoke("LangGraphを一言で説明して")
print(response.content)