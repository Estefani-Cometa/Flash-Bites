import os
from pathlib import Path
from typing import Any

try:
    from langchain_community.document_loaders import CSVLoader, PyPDFLoader
    from langchain_community.vectorstores import Chroma
    from langchain_core.embeddings import FakeEmbeddings
    from langchain_openai import OpenAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:  # pragma: no cover - fallback for environments without langchain
    CSVLoader = PyPDFLoader = Chroma = None
    FakeEmbeddings = OpenAIEmbeddings = RecursiveCharacterTextSplitter = None

from app.core.config import settings


class RAGService:
    """Servicio simple de RAG para responder preguntas usando documentos."""

    def __init__(self) -> None:
        self.persist_directory = Path(settings.chroma_persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.documents_dir = Path(settings.documents_directory)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings = None
        self.text_splitter = None
        if OpenAIEmbeddings is not None and FakeEmbeddings is not None and RecursiveCharacterTextSplitter is not None:
            self.embeddings = (
                OpenAIEmbeddings(api_key=settings.openai_api_key or os.getenv("OPENAI_API_KEY"))
                if settings.openai_api_key or os.getenv("OPENAI_API_KEY")
                else FakeEmbeddings(size=1536)
            )
            self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    def ingest_documents(self) -> None:
        if self.embeddings is None or self.text_splitter is None or Chroma is None or CSVLoader is None or PyPDFLoader is None:
            return
        documents = []
        for file_path in self.documents_dir.glob("*"):
            if file_path.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(file_path))
            elif file_path.suffix.lower() == ".csv":
                loader = CSVLoader(str(file_path))
            else:
                continue
            documents.extend(loader.load())
        if not documents:
            return
        chunks = self.text_splitter.split_documents(documents)
        Chroma.from_documents(chunks, self.embeddings, persist_directory=str(self.persist_directory))

    def answer_question(self, question: str) -> str:
        if self.embeddings is None or Chroma is None:
            return "El módulo de RAG está listo para integrarse con documentos reales cuando se habiliten las dependencias de IA."
        db = Chroma(persist_directory=str(self.persist_directory), embedding_function=self.embeddings)
        docs = db.similarity_search(question, k=3)
        if not docs:
            return "No tengo información aún sobre ese tema."
        context = "\n\n".join(doc.page_content for doc in docs)
        return f"Contexto relevante:\n{context[:1500]}"


rag_service = RAGService()
