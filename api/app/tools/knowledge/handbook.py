from langchain.tools import tool
from langchain_qdrant import QdrantVectorStore

from app.schemas.retrieval import Source

def file_search( store: QdrantVectorStore, top_k: int) -> Basetool:
    @tool(response_format="content_and_artifact")
    def search_handbook(query: str) -> None:
        """Search the Clause shop handbook for passages relevant to the query.

        Args:
            query: A short, specific search phrase (e.g. "return policy for opened items" or "standard shipping time").
        """
        
        results= store.similarity_search_with_score(
            query=query, k=top_k
        )
        if not results:
            return "Nothing Founds", []


        text = "\n\n".join(doc.page_content for doc, _ in results)
        sources=[
             Source(
                    source=doc.metadata.get("source", "unknown"),
                    page=doc.metadata.get("page"),
                    score=round(score, 4)
                )
                for doc, score in results
        ]


        return text, sources

    return search_handbook
