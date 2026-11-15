# Ingestion---? Perform Just One Time -- Rerun only when any change in document
# 1. load- Loading Document (.doc,.pdf,.csv,.sql,.html) 2. chunks 3. Embed 4. Store
from pathlib import Path

# from pypdf import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from qdrant_client.models import Distance, VectorParams, SparseVectorParams

from app.core.config import get_embeddings, get_qdrant_client, get_settings


def load(path: Path) -> list[Document]: # Return List Of Documents # Langchain Class "Documents"->its attributes-> Page_content,Meta_Data,id
    return PyPDFLoader(path).load()

def ingest(path: str | None = None) -> int:
    settings = get_settings()

    # 1. Load
    file = Path(path or settings.data_path)
    documents = load(file)

    # 2. Chunk
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)   # splitting Chunks
    if not chunks:
        raise ValueError(f"No text found in {file}")

    # 3. Embed: check the model works before the old collection is deleted
    embed = get_embeddings(settings)    # Converting chunks into Vectors

    actual_dim = len(embed.embed_query("dimension check"))
    if actual_dim != settings.embed_dim:
        raise ValueError(
            f"RAG_EMBED_DIM is {settings.embed_dim}, "
            f"but {settings.embed_model} returns {actual_dim} dimensions"
        )

    # 4. Store
    client = get_qdrant_client(settings)

    try:
        if client.collection_exists(settings.collection_name):
            client.delete_collection(settings.collection_name)
 # Table Creation/collection
        client.create_collection(
            collection_name=settings.collection_name,
            vectors_config={"dense": VectorParams(size=settings.embed_dim, distance=Distance.COSINE)},
            sparse_vectors_config={"sparse": SparseVectorParams()}
        )

# Storing chunks in collection vector databse using this model
# Same changes in chat.py and rerun ingest file

        vector_store = QdrantVectorStore(
            client=client,
            collection_name=settings.collection_name,
            embedding=embed,
            sparse_embedding=FastEmbedSparse(model_name="Qdrant/bm25"),
            retrieval_mode=RetrievalMode.HYBRID,    # by default:Dense
            vector_name="dense",
            sparse_vector_name="sparse"
        )
        vector_store.add_documents(chunks)
    finally:
        client.close()

    return len(chunks)


if __name__ == "__main__":
    print(ingest(), "chunks indexed")

# cd api
# uv run python -m app.services.ingestion

