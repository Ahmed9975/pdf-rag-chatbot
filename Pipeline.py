from __future__ import annotations

import hashlib
import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DEFAULT_RETRIEVAL_K,
    DEVICE,
    EMBEDDING_MODEL,
    INDEX_ROOT,
    MAX_HISTORY_TURNS,
)


class Pipeline:
    def __init__(self, file_path: str, verbose: bool = False):
        self.file_path = file_path
        self.file_name = Path(file_path).stem
        self.verbose = verbose
        self.documents = None
        self.chunks = None
        self.embeddings = None
        self.vector_store = None
        self.history: list[tuple[str, str]] = []

        os.makedirs(INDEX_ROOT, exist_ok=True)
        file_key = hashlib.md5(str(Path(file_path).resolve()).encode()).hexdigest()[:8]
        self.index_path = os.path.join(INDEX_ROOT, f"{self.file_name}_{file_key}_index")

    def _log(self, title: str, content: str) -> None:
        if self.verbose:
            print(f"\n{'=' * 60}\n{title}\n{'=' * 60}\n{content}")

    def load_file(self):
        if self.documents is None:
            loader = PyPDFLoader(self.file_path)
            self.documents = loader.load()
            self._log("PDF LOADED", f"Loaded {self.file_name}")
        return self.documents

    def split_documents(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ):
        self.load_file()
        if self.chunks is None:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            self.chunks = text_splitter.split_documents(self.documents)
            self._log(
                "DOCUMENTS SPLIT",
                f"Chunk size: {chunk_size} | overlap: {chunk_overlap} | total chunks: {len(self.chunks)}",
            )
        return self.chunks

    def ensure_embeddings(self):
        if self.embeddings is None:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={"device": DEVICE},
            )
        return self.embeddings

    def build_vector_store(self):
        if self.vector_store is not None:
            return self.vector_store

        self.ensure_embeddings()
        self.split_documents()

        if os.path.exists(self.index_path):
            self.vector_store = FAISS.load_local(
                self.index_path,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            self._log("VECTOR STORE", f"Loaded existing FAISS index for {self.file_name}")
        else:
            self.vector_store = FAISS.from_documents(self.chunks, self.embeddings)
            self.vector_store.save_local(self.index_path)
            self._log("VECTOR STORE", f"Created new FAISS index for {self.file_name}")

        return self.vector_store

    def ensure_ready(self):
        self.load_file()
        self.split_documents()
        self.build_vector_store()
        return self

    def add_history_turn(self, question: str, answer: str) -> None:
        self.history.append((question, answer))
        if len(self.history) > MAX_HISTORY_TURNS:
            self.history = self.history[-MAX_HISTORY_TURNS:]

    def retrieve_context(self, question: str, k: int = DEFAULT_RETRIEVAL_K) -> str:
        self.ensure_ready()
        prefixed_question = (
            "Instruct: Given a question, retrieve relevant passages\n"
            f"Query: {question}"
        )
        matched_docs = self.vector_store.similarity_search_with_score(prefixed_question, k=k)

        if not matched_docs:
            self._log("RETRIEVED CHUNKS", "(none found)")
            return "No relevant context found in the uploaded document."

        context_parts: list[str] = []
        log_chunks: list[str] = []
        for index, (doc, chunk_score) in enumerate(matched_docs, start=1):
            context_parts.append(doc.page_content)
            preview = doc.page_content[:300].replace("\n", " ")
            if len(doc.page_content) > 300:
                preview += "..."
            log_chunks.append(
                f"[Chunk {index}] Page: {doc.metadata.get('page', 'N/A')} | Score: {chunk_score:.4f}\n{preview}"
            )

        self._log("RETRIEVED CHUNKS", "\n\n".join(log_chunks))
        return "\n\n".join(context_parts)
