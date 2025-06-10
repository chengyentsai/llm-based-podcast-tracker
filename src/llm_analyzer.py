import os
from langchain_core.output_parsers import PydanticOutputParser
from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate

# 從我們的資料模型檔案中導入定義好的結構
from .data_models import MentionsList

def create_llm_analyzer_chain():
    """
    建立並返回一個 LangChain 處理鏈 (Chain)。
    這個 Chain 負責接收 podcast 逐字稿，並回傳結構化的股票提及資訊。
    
    整個流程被封裝起來，展示了模組化和可重用性。
    """
    # 1. 初始化 Bedrock LLM 模型
    # 假設 AWS 憑證已透過環境變數或 IAM Role 設定好
    model = ChatBedrock(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        model_kwargs={"temperature": 0.1, "max_tokens": 4096},
        region_name=os.environ.get("AWS_REGION_NAME", "us-east-1")
    )

    # 2. 建立一個基於 Pydantic 模型的輸出解析器
    parser = PydanticOutputParser(pydantic_object=MentionsList)

    # 3. 設計一個清晰的提示詞模板 (Prompt Template)
    #    - {transcript}: 將會被傳入的逐字稿內容
    #    - {format_instructions}: LangChain 會自動填入 Pydantic 模型的格式要求
    prompt = PromptTemplate(
        template="""You are an expert financial analyst. Your task is to identify all mentions of publicly traded companies and their stock tickers from the following podcast transcript.
Provide a list of all mentions you find.

{format_instructions}

Here is the podcast transcript:
---
{transcript}
---
""",
        input_variables=["transcript"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    # 4. 使用 LangChain Expression Language (LCEL) 將各個組件串連起來
    #    這是一個非常現代且強大的做法，流程清晰可見：
    #    Prompt -> Model -> Parser
    chain = prompt | model | parser
    
    return chain

if __name__ == '__main__':
    # 這段程式碼讓此檔案可以被獨立執行以進行快速測試
    
    # 建立處理鏈
    analyzer_chain = create_llm_analyzer_chain()

    # 模擬一份 podcast 逐字稿
    sample_transcript = """
    ...so then we were talking about the AI boom, and of course, NVIDIA is just on a tear. 
    Their stock, NVDA, seems to be unstoppable. I think it's a great long term hold. 
    On the other hand, some people are still skeptical.
    Later in the show, we also touched on Apple's new product launch. I'm not so sure about the Vision Pro. 
    The market seems hesitant, and the AAPL stock reflects that uncertainty. It's pretty neutral for now.
    """

    print("正在使用 LangChain 分析範例逐字稿...")
    
    try:
        # 執行 Chain
        result = analyzer_chain.invoke({"transcript": sample_transcript})
        
        # `result` 已經是一個漂亮的 Pydantic 物件，而不是混亂的 JSON 字串
        print("\n✅ 分析成功！已提取出結構化資料：")
        for mention in result.mentions:
            print("-" * 20)
            print(f"公司: {mention.company_name} ({mention.stock_ticker})")
            print(f"情緒: {mention.sentiment}")
            print(f"時間戳(秒): {mention.timestamp_seconds}")
            print(f"上下文: {mention.context_snippet}")

    except Exception as e:
        print(f"\n❌ 分析失敗: {e}")
