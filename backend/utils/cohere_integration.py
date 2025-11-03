from langchain_cohere import ChatCohere
from config import COHERE_API_KEY, LLM_MODEL

def get_llm():
    return ChatCohere(model=LLM_MODEL, cohere_api_key="W9T9D3DGjtqAEgPEAJlr0J8GWYMLDwSNm4EqYi3Y")
