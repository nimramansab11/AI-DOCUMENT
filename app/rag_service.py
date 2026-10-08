from pathlib import Path
import chromadb

from .embeddings import EmbeddingService
from .ingestion import DocumentIngestion


class RAGService:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent

        self.documents_dir = self.base_dir / "documents"
        self.chroma_dir = self.base_dir / "chroma_db"

        self.embedding_service = EmbeddingService()
        self.ingestion_service = DocumentIngestion(
            chunk_size=1000,
            chunk_overlap=150
        )

        self.client = chromadb.PersistentClient(
            path=str(self.chroma_dir)
        )

        self.collection = self.client.get_or_create_collection(
            name="document_knowledge_base"
        )

    def ingest_documents(self):
        """Load documents, create chunks, generate embeddings and store them."""

        files = list(self.documents_dir.glob("*.pdf"))
        files += list(self.documents_dir.glob("*.txt"))
        files += list(self.documents_dir.glob("*.md"))

        if not files:
            raise ValueError(
                "No PDF, TXT, or Markdown documents found."
            )

        total_chunks = 0

        for file_path in files:
            print(f"Processing: {file_path.name}")

            text = self.ingestion_service.load_document(
                file_path
            )

            chunks = self.ingestion_service.chunk_text(text)

            if not chunks:
                print(f"No text found in {file_path.name}")
                continue

            embeddings = self.embedding_service.embed_documents(
                chunks
            )

            ids = [
                f"{file_path.stem}_{index}"
                for index in range(len(chunks))
            ]

            metadatas = [
                {
                    "source": file_path.name,
                    "chunk": index + 1
                }
                for index in range(len(chunks))
            ]

            self.collection.upsert(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas
            )

            total_chunks += len(chunks)

        return total_chunks

    def search(self, question, top_k=3):
        """Retrieve the most relevant document chunks."""

        question_embedding = (
            self.embedding_service.embed_query(question)
        )

        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        retrieved_chunks = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):
            retrieved_chunks.append(
                {
                    "content": document,
                    "source": metadata.get("source"),
                    "chunk": metadata.get("chunk"),
                    "distance": distance
                }
            )

        return retrieved_chunks

    def get_context(self, question, top_k=3):
        """Create context from retrieved chunks."""

        results = self.search(
            question,
            top_k=top_k
        )

        context_parts = []

        for item in results:
            context_parts.append(
                f"Source: {item['source']}\n"
                f"Chunk: {item['chunk']}\n"
                f"Content:\n{item['content']}"
            )

        return "\n\n---\n\n".join(context_parts)

    def count(self):
        return self.collection.count()