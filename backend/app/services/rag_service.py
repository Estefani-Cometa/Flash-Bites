import os
from pathlib import Path

try:
    from langchain_community.document_loaders import (
        CSVLoader,
        PyPDFLoader,
        TextLoader,
    )
    from langchain_community.vectorstores import Chroma
    from langchain_core.embeddings import FakeEmbeddings
    from langchain_openai import OpenAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    CSVLoader = None
    PyPDFLoader = None
    TextLoader = None
    Chroma = None
    FakeEmbeddings = None
    OpenAIEmbeddings = None
    RecursiveCharacterTextSplitter = None

from app.core.config import settings


class RAGService:
    """
    Servicio encargado de:
    - Leer documentos
    - Crear la base vectorial
    - Buscar información relacionada
    """

    def __init__(self):

        self.persist_directory = Path(settings.chroma_persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.documents_dir = Path(settings.documents_directory)
        self.documents_dir.mkdir(parents=True, exist_ok=True)

        self.embeddings = None
        self.text_splitter = None

        if (
            OpenAIEmbeddings
            and FakeEmbeddings
            and RecursiveCharacterTextSplitter
        ):

            if settings.openai_api_key or os.getenv("OPENAI_API_KEY"):

                print("🤖 OpenAI Embeddings")

                self.embeddings = OpenAIEmbeddings(
                    api_key=settings.openai_api_key
                    or os.getenv("OPENAI_API_KEY")
                )

            else:

                print("🧠 Fake Embeddings (Modo Desarrollo)")

                self.embeddings = FakeEmbeddings(size=1536)

            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=100,
            )

    # --------------------------------------------------------

    def ingest_documents(self):

        if (
            self.embeddings is None
            or self.text_splitter is None
            or Chroma is None
        ):
            return

        documents = []

        print("\n========== DOCUMENTOS ==========\n")

        for file in self.documents_dir.glob("*"):

            try:

                print(f"Leyendo {file.name}")

                if file.suffix.lower() == ".pdf":

                    loader = PyPDFLoader(str(file))

                elif file.suffix.lower() == ".csv":

                    loader = CSVLoader(str(file))

                elif file.suffix.lower() == ".txt":

                    loader = TextLoader(
                        str(file),
                        encoding="utf-8",
                    )

                else:
                    continue

                documents.extend(loader.load())

            except Exception as e:

                print(e)

        if not documents:

            print("No hay documentos")

            return

        chunks = self.text_splitter.split_documents(documents)

        Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=str(self.persist_directory),
        )

        print(f"Base vectorial creada ({len(chunks)} fragmentos)\n")

    # --------------------------------------------------------

    def search(self, question):

        if self.embeddings is None or Chroma is None:
            return []

        db = Chroma(
            persist_directory=str(self.persist_directory),
            embedding_function=self.embeddings,
        )

        return db.similarity_search(question, k=5)

    # --------------------------------------------------------

    def answer_question(self, question):

        docs = self.search(question)

        if not docs:

            return "No encontré información relacionada."

        return docs

    # --------------------------------------------------------

    def initialize(self):

        try:

            self.ingest_documents()

        except Exception as e:

            print(e)


rag_service = RAGService()
rag_service.initialize()