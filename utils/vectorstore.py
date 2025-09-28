# utils/vectorstore.py

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = BASE_DIR / "vector_db"

load_dotenv(BASE_DIR / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ---------- Build Vectorstore ----------
def build_vectorstore(persist_directory: Path = VECTOR_DB_DIR):
    """
    Loads all PDFs from /data, chunks them, embeds them, and stores them in ChromaDB.
    """
    print("📚 Loading PDF documents...")
    pdf_files = list(DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError("No PDF files found in the /data directory.")

    documents = []
    for pdf_file in pdf_files:
        print(f"📄 Loading: {pdf_file.name}")
        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()
        documents.extend(docs)

    print(f"✅ Loaded {len(documents)} documents")

    # Split into smaller chunks
    print("✂️ Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " "]
    )
    split_docs = splitter.split_documents(documents)
    print(f"📚 Split into {len(split_docs)} chunks")

    # Create embeddings
    print("🧠 Generating embeddings...")
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    # Create Chroma vector store
    print("💾 Storing embeddings in Chroma vector DB...")
    vectordb = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=str(persist_directory)
    )

    vectordb.persist()
    print("✅ Vectorstore built successfully and saved to /vector_db")

# ---------- Load Vectorstore ----------
def load_vectorstore(persist_directory: Path = VECTOR_DB_DIR) -> Chroma:
    """
    Loads the existing vector store from disk.
    """
    print("📥 Loading vectorstore...")
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectordb = Chroma(
        persist_directory=str(persist_directory),
        embedding_function=embeddings
    )
    return vectordb

# ---------- Search Function ----------
def search_policy(query: str, k: int = 3) -> List[str]:
    """
    Performs a semantic search on the vector DB and returns top policy sections.
    """
    vectordb = load_vectorstore()
    results = vectordb.similarity_search(query, k=k)
    return [doc.page_content for doc in results]

# ---------- CLI Entry Point ----------
if __name__ == "__main__":
    build_vectorstore()
    print("✅ Done. You can now query policies using search_policy().")
