from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

class StockMention(BaseModel):
    """
    定義單一股票提及事件的資料結構。
    這個模型被用作 LangChain PydanticOutputParser 的藍圖，
    以確保 LLM 的回覆是結構化且可驗證的。
    """
    company_name: str = Field(description="提及的公司全名，例如 'NVIDIA Corporation'")
    stock_ticker: str = Field(description="對應的股票代碼，例如 'NVDA'")
    timestamp_seconds: int = Field(description="在音檔中被提及的大約時間點(秒)")
    sentiment: str = Field(description="對該股票的情緒分析，應為 'POSITIVE', 'NEUTRAL', 或 'NEGATIVE'")
    context_snippet: str = Field(
        description="提及該公司時，包含上下文的逐字稿片段(約1-2句話)",
        min_length=20  # 增加一些驗證規則
    )

class MentionsList(BaseModel):
    """
    定義一個包含多次股票提及的列表。
    這是 LLM 最終應該回傳的頂層物件。
    """
    mentions: List[StockMention] = Field(
        description="在逐字稿中找到的所有股票提及的列表"
    )
