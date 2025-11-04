import os
from typing import Dict, List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_cohere import ChatCohere
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from utils.cohere_integration import get_llm   

PDF_PATH = "agents/fictional_company_policies_handbook.pdf"
DB_PATH = "backend/data/policies"

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
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
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        vectordb = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=DB_PATH)
        vectordb.persist()
    else:
        vectordb = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    return vectordb

vectordb = _create_or_load_vectorstore()
retriever = vectordb.as_retriever(search_kwargs={"k": 6})

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

def policy_chatbot_agent(payload: Dict) -> Dict:
    question = payload.get("question", "").strip()
    if not question:
        return {"error": "Missing 'question' in payload"}
    try:
        result = qa_chain.invoke({"query": question})
        answer = result["result"]
        sources = []
        seen = set()
        for doc in result["source_documents"]:
            src = doc.metadata["source"]
            page = doc.metadata.get("page")
            key = (src, page)
            if key not in seen and page:
                sources.append(f"{src} (p. {page})")
                seen.add(key)
        return {
            "answer": answer,
            "sources": sources or ["Fictional Company Policies Handbook"]
        }
    except Exception as e:
        return {"error": str(e)}
