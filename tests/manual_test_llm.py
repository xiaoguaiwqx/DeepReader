import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from deep_reader.intelligence.llm_client import LLMClient

def test_llm():
    load_dotenv()
    
    print("Initializing LLM Client...")
    
    # Optional: Set these for manual testing if .env is not set
    # os.environ["LLM_PROVIDER"] = "custom"
    # os.environ["LLM_API_KEY"] = "sk-..."
    # os.environ["LLM_BASE_URL"] = "https://api.siliconflow.cn/v1"
    # os.environ["LLM_MODEL"] = "deepseek-ai/DeepSeek-V3"
    
    try:
        llm = LLMClient()
        print(f"Provider: {llm.provider}")
        if llm.provider == "custom":
            print(f"Base URL: {llm.base_url}")
            print(f"Model: {llm.model_name}")
    except Exception as e:
        print(f"Failed to init: {e}")
        return

    if (llm.provider == "google" and not llm.model) or (llm.provider in ["custom", "openai"] and not llm.client):
        print("LLM model not initialized (API Key missing?). Skipping generation.")
        return

    text = """
    We introduce DeepReader, an automated system for tracking research papers.
    It uses Large Language Models to summarize papers and a local database to store them.
    The system is designed to help researchers keep up with the latest advancements in AI.
    """
    
    print("Testing summary generation...")
    summary = llm.generate_summary(text)
    print("\n--- Summary ---")
    print(summary)
    print("---------------\n")

if __name__ == "__main__":
    test_llm()
