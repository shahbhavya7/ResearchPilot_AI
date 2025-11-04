# rag_pipeline.py
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from src.gemini_wrapper import call_gemini 
from langchain.prompts import PromptTemplate
import os

def create_or_load_vectorstore(pdf_dir="data"):
    from src.pdf_loader import extract_text_from_pdf, chunk_text
    from langchain.embeddings import SentenceTransformerEmbeddings
    from langchain.vectorstores import FAISS
    import shutil, os

    embedder = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # ✅ Step 1: clear old vectorstore before creating new
    if os.path.exists("vectorstore"):
        shutil.rmtree("vectorstore")  # deletes old FAISS index

    all_texts = []
    metadatas = []

    for pdf in os.listdir(pdf_dir):
        if pdf.endswith(".pdf"):
            path = os.path.join(pdf_dir, pdf)
            text = extract_text_from_pdf(path)
            chunks = chunk_text(text)
            all_texts.extend(chunks)
            metadatas.extend([{"source": pdf}] * len(chunks))

    # ✅ Step 2: build new FAISS store only for uploaded PDFs
    db = FAISS.from_texts(all_texts, embedder, metadatas=metadatas)
    db.save_local("vectorstore")

    return db


def load_vectorstore():
    embedder = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.load_local("vectorstore", embedder, allow_dangerous_deserialization=True)

def get_qa_chain():
    db = load_vectorstore()
    retriever = db.as_retriever(search_kwargs={"k": 4})

    def qa_function(question: str):
        # Retrieve top chunks
        docs = retriever.get_relevant_documents(question)
        context = "\n\n".join([f"[{d.metadata['source']}]\n{d.page_content}" for d in docs])
        # Call Gemini model
        answer = call_gemini(question, context)
        return answer

    return qa_function
