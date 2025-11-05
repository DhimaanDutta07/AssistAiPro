import os
from typing import Dict, List
from langchain_community.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from utils.cohere_integration import get_llm

PDF_PATH = "agents/fictional_company_policies_handbook.pdf"
DB_PATH = "backend/data/policies"

embeddings = CohereEmbeddings(
    model="embed-english-light-v3.0",
    cohere_api_key="W9T9D3DGjtqAEgPEAJlr0J8GWYMLDwSNm4EqYi3Y"
)
llm = get_llm()

def _load_pdf_documents() -> List[Document]:
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
        vectordb = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=DB_PATH)
        vectordb.persist()
    else:
        vectordb = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    return vectordb

vectordb = _create_or_load_vectorstore()
retriever = vectordb.as_retriever(search_kwargs={"k": 4})

def policy_chatbot_agent(payload: Dict) -> Dict:
    question = payload.get("question", "").strip()
    if not question:
        return {"error": "Missing 'question' in payload"}
    try:
        results = retriever.get_relevant_documents(question)
        if not results:
            return {"answer": "Sorry, I couldn't find anything related.", "sources": []}
        context = "\n\n".join([doc.page_content for doc in results])
        prompt = f"Answer the following question using the context:\n\nContext:\n{context}\n\nQuestion: {question}"
        response = llm.invoke(prompt)
        sources = []
        seen = set()
        for doc in results:
            src = doc.metadata.get("source")
            page = doc.metadata.get("page")
            key = (src, page)
            if key not in seen and page:
                sources.append(f"{src} (p. {page})")
                seen.add(key)
        return {
            "answer": getattr(response, "content", str(response)),
            "sources": sources or ["Fictional Company Policies Handbook"]
        }
    except Exception as e:
        return {"error": str(e)}
