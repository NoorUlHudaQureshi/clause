# AGENTIC RAG # Retrieval Engine
import sqlite3

from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from app.services.chat import RAGService

from app.prompts.loaders import get_prompt

conn = sqlite3.connect(database="memory.db", check_name_thread=False)
checkpointer = SqliteSaver(conn)

class ClauseAgent:
    def __init__(self) -> None:
        self.rag = RAGService()  # instance attribute - composition - (RAGservices type Object) Composition - compulsory, Aggregation - optional
        
        @tool(response_format="content_and_artifact")
        def search_handbook(query: str) -> None:
            """Search the Clause shop handbook for passages relevant to the query.

            Use this for any customer question about products, orders, shipping,
            returns, payments, or shop policies. Do not answer such questions from memory.

            Args:
                query: A short, specific search phrase based on the customer's question,
                e.g. "return window for opened items" or "standard shipping time".

            Returns:
                Matching handbook passages, each prefixed with its page number as
                "[page N]". If nothing relevant is found, says so.
            """
            
            results= self.rag.store.similarity_search_with_score(
                query=query, k=self.rag.settings.top_k
            )
            if not results:
                return "Nothing Founds", []

            texts = []
            sources = []
            for doc, score in results:
                text.append(doc.page_content)
                sources.append({"page": doc.metadata.get("page"), "score": round(number=score, ndigits=4)})
            text = "\n\n".join(texts)

            return text, sources
        
        self.agent = create_agent(
        model=self.rag.llm,
        tools=[search_handbook],
        system_prompt=get_prompt(name="support/system", version=self.rag.settings.system_prompt_version),
        checkpointer=checkpointer
        
        )

    # Agent ...

    def ask(self, question: str, thread_id: str) -> dict[str, any]:
        result = self.agent.invoke(input={"messages": [HumanMessage(content=question)]})

        messages = result["messages"]
        sources: list[dict] = []
        searches: list[str] = []

        for message in messages:
            if isinstance(message, AIMessage):
                for call in message.tool_calls:
                    if call["name"] == "search_handbook":
                        searches.append(call["args"].get("query", ""))
            elif isinstance(message, ToolMessage) and message.name == "search_handbook":
                sources.extend(message.artifact or [])

        return {
            "answer": messages[-1].text,
            "searches": searches,
            "sources": sources,
        }

    def close(self) -> None:
        self.rag.close()




# print(response["response"][-1].text)