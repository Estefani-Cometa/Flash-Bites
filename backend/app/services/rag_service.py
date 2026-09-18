import logging
import os
from pathlib import Path

try:
    from langchain_community.document_loaders import (
        CSVLoader,
        PyPDFLoader,
        TextLoader,
    )
    from langchain_community.vectorstores import Chroma
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    CSVLoader = None
    PyPDFLoader = None
    TextLoader = None
    Chroma = None
    GoogleGenerativeAIEmbeddings = None
    RecursiveCharacterTextSplitter = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """
    Servicio encargado de:

    • Leer documentos
    • Crear la base vectorial
    • Buscar información relacionada
    """

    def __init__(self):
        self.persist_directory = Path(settings.chroma_persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.documents_dir = Path(settings.documents_directory)
        self.documents_dir.mkdir(parents=True, exist_ok=True)

        self.embeddings = None
        self.text_splitter = None

        if (
            GoogleGenerativeAIEmbeddings
            and RecursiveCharacterTextSplitter
        ):
            api_key = (
                settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
            )
            if api_key:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/gemini-embedding-001",
                    google_api_key=api_key,
                )
            else:
                logger.warning("No se encontró GEMINI_API_KEY para RAG")

            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=100,
            )

    def _dependencies_available(self) -> bool:
        return (
            self.embeddings is not None
            and self.text_splitter is not None
            and Chroma is not None
        )

    def _normalize_content(self, content: str) -> str:
        return " ".join(content.strip().split())

    def ingest_documents(self) -> None:
        if not self._dependencies_available():
            return

        documents = []

        if not self.documents_dir.exists():
            logger.warning(
                "El directorio de documentos RAG no existe: %s",
                self.documents_dir,
            )
            return

        for file in self.documents_dir.glob("*"):
            try:
                if file.suffix.lower() == ".pdf":
                    loader = PyPDFLoader(str(file))
                elif file.suffix.lower() == ".csv":
                    loader = CSVLoader(str(file))
                elif file.suffix.lower() == ".txt":
                    loader = TextLoader(str(file), encoding="utf-8")
                else:
                    continue

                documents.extend(loader.load())
            except Exception:
                logger.exception("Error leyendo documento %s", file.name)

        if not documents:
            logger.info("No hay documentos para RAG")
            return

        chunks = self.text_splitter.split_documents(documents)

        unique_chunks = []
        seen = set()
        for chunk in chunks:
            normalized = self._normalize_content(chunk.page_content)
            if normalized in seen:
                continue
            seen.add(normalized)
            chunk.page_content = chunk.page_content.strip()
            chunk.metadata["tenant_id"] = settings.tenant_id
            unique_chunks.append(chunk)

        Chroma.from_documents(
            documents=unique_chunks,
            embedding=self.embeddings,
            persist_directory=str(self.persist_directory),
        )

        logger.info(
            "Base vectorial creada (%d fragmentos)",
            len(unique_chunks),
        )

    def search(
        self,
        question: str,
        k: int = 3,
        tenant_id: int | None = None,
    ) -> list[object]:
        if not self._dependencies_available():
            return []

        try:
            db = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings,
            )
            docs = db.similarity_search(
                question,
                k=k,
                filter={"tenant_id": tenant_id or settings.tenant_id},
            )
        except Exception:
            logger.exception("Error buscando en RAG")
            return []

        results = []
        seen = set()
        for doc in docs:
            contenido = self._normalize_content(doc.page_content)
            if contenido in seen:
                continue
            seen.add(contenido)
            results.append(doc)

        return results

rag_service = RAGService()