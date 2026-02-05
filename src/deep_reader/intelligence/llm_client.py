import os
import google.generativeai as genai
from typing import Optional
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class LLMClient:
    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None, base_url: Optional[str] = None, model_name: Optional[str] = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "google")
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.model_name = model_name or os.getenv("LLM_MODEL")
        
        self.client = None
        self.model = None

        if self.provider == "google":
            if not self.api_key:
                print("Warning: LLM_API_KEY (or GEMINI_API_KEY) not found. LLM features will be disabled.")
            else:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
        
        elif self.provider in ["custom", "openai"]:
            if not OpenAI:
                raise ImportError("openai package is required for custom provider. Install it with `pip install openai`.")
            
            if not self.api_key:
                print("Warning: LLM_API_KEY not found. LLM features will be disabled.")
            else:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url  # Optional for OpenAI, required for some custom providers
                )
                self.model_name = self.model_name or "gpt-3.5-turbo" # Default fallback
                
        else:
            raise NotImplementedError(f"Provider {self.provider} not supported yet.")

    def generate_summary(self, text: str) -> str:
        prompt = f"""
        You are an expert academic researcher. Please provide a structured summary of the following research paper abstract in Chinese.
        
        Structure your response exactly as follows:
        1. **Problem Definition**: What problem is this paper trying to solve?
        2. **Methodology**: How did they solve it?
        3. **Key Results**: What did they find?
        4. **Limitations**: Any mentioned limitations?

        Abstract:
        {text}
        """

        try:
            if self.provider == "google":
                if not self.model:
                    return "Summary unavailable (LLM not configured)."
                response = self.model.generate_content(prompt)
                return response.text
            
            elif self.provider in ["custom", "openai"]:
                if not self.client:
                    return "Summary unavailable (LLM not configured)."
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful research assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
                
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Summary generation failed: {e}"
