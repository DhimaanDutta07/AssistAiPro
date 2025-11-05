import os
from typing import Dict, List
from langchain_community.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from utils.cohere_integration import get_llm

PDF_PATH = "fictional_company_policies_handbook.pdf"
DB_PATH = "data/policies"

embeddings = CohereEmbeddings(
    model="embed-english-light-v3.0",
    cohere_api_key=os.getenv("COHERE_API_KEY")
)

llm = get_llm()

def _load_pdf_documents() -> List:
    loader = PyPDFLoader(PDF_PATH)
    pages = loader.load()
    for i, page in enumerate(pages):
        page.metadata["page"] = i + 1
        page.metadata["source"] = os.path.basename(PDF_PATH)
    return pages

def _create_or_load_vectorstore() -> Chroma:
    os.makedirs(DB_PATH, exist_ok=True)
    if not os.listdir(DB_PATH):
        docs = _load_pdf_documents()
        vectordb = Chroma.from_documents(docs, embedding=embeddings, persist_directory=DB_PATH)
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
        results = vectordb.similarity_search(question, k=4)
        if not results:
            return {"answer": "Sorry, no relevant info found.", "sources": []}

        context = "\n\n".join([doc.page_content for doc in results])
        prompt = f"Answer the question using the following context:\n\n{context}\n\nQuestion: {question}"
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
