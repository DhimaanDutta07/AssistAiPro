import os
from typing import Dict, List
from langchain_community.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from utils.cohere_integration import get_llm

PDF_PATH = os.path.join(os.path.dirname(__file__), "fictional_company_policies_handbook.pdf")
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/policies")

embeddings = CohereEmbeddings(
    model="embed-english-light-v3.0",
    cohere_api_key="W9T9D3DGjtqAEgPEAJlr0J8GWYMLDwSNm4EqYi3Y"
)

llm = get_llm()

def _load_pdf_documents() -> List:
    if not os.path.exists(PDF_PATH):
        return []
    loader = PyPDFLoader(PDF_PATH)
    pages = loader.load()
    for i, page in enumerate(pages):
        page.metadata["page"] = i + 1
        page.metadata["source"] = os.path.basename(PDF_PATH)
    return pages

def _create_or_load_vectorstore() -> Chroma:
    os.makedirs(DB_PATH, exist_ok=True)
    docs = _load_pdf_documents()
    if docs:
        if not os.listdir(DB_PATH):
            vectordb = Chroma.from_documents(docs, embedding=embeddings, persist_directory=DB_PATH)
            vectordb.persist()
        else:
            vectordb = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        return vectordb
    return None

vectordb = _create_or_load_vectorstore()

TEMPLATE_PROMPT = (
    "You are an AI assistant for HR and company policies. "
    "Do not say you don't know or reference unavailable company resources. "
    "If no specific company data is provided, assume a fictional company and "
    "create logical, professional policies yourself. "
    "Answer questions about leave, resignation, performance, or any HR topic "
    "by generating coherent policies based on common corporate practices."
)

def policy_chatbot_agent(payload: Dict) -> Dict:
    question = payload.get("question", "").strip()
    if not question:
        return {"error": "Missing 'question' in payload"}
    try:
        if vectordb:
            results = vectordb.similarity_search(question, k=4)
        else:
            results = []

        if results:
            context = "\n\n".join([doc.page_content for doc in results])
            prompt = f"{TEMPLATE_PROMPT}\n\nUse this context:\n{context}\n\nQuestion: {question}"
        else:
            prompt = f"{TEMPLATE_PROMPT}\n\nQuestion: {question}"

        response = llm.invoke(prompt)

        sources = []
        if results:
            seen = set()
            for doc in results:
                src = doc.metadata.get("source")
                page = doc.metadata.get("page")
                key = (src, page)
                if key not in seen and page:
                    sources.append(f"{src} (p. {page})")
                    seen.add(key)
        if not sources:
            sources = ["Generated fictional company policy"]

        return {
            "answer": getattr(response, "content", str(response)),
            "sources": sources
        }

    except Exception as e:
        return {"error": str(e)}
