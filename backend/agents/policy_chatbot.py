import os
from typing import Dict, List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import CohereEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from utils.cohere_integration import get_llm

PDF_PATH = "agents/fictional_company_policies_handbook.pdf"
DB_PATH = "backend/data/policies"

embeddings = CohereEmbeddings(
    model="small",                
    api_key=os.environ["COHERE_API_KEY"]
)
llm = get_llm()

def _load_pdf_documents() -> List:
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF not found at {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    pages = loader.load()
    for i, page in enumerate(pages):
        page.metadata["page"] = i + 1
        page.metadata["source"] = os.path.basename(PDF_PATH)
    return pages

def _create_or_load_vectorstore() -> Chroma:
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
    if not os.listdir(DB_PATH):
        docs = _load_pdf_documents()
        vectordb = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=DB_PATH
        )
        vectordb.persist()
    else:
        vectordb = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    return vectordb

vectordb = _create_or_load_vectorstore()

def policy_chatbot_agent(payload: Dict) -> Dict:
    question = payload.get("question", "").strip()
    if not question:
        return {"error": "Missing 'question' in payload"}

    try:
        results = vectordb.similarity_search(question, k=3)
        if not results:
            return {"answer": "No relevant information found.", "sources": []}

        answer = "\n".join([doc.page_content for doc in results])
        sources = [f"{doc.metadata.get('source')} (p. {doc.metadata.get('page')})" for doc in results]

        return {
            "answer": answer,
            "sources": sources or ["Fictional Company Policies Handbook"]
        }

    except Exception as e:
        return {"error": str(e)}
