# AGENTIC RAG # Retrieval Engine
import sqlite3

from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.checkpoint.sqlite import SqliteSaver

# from app.services.chat import RAGService
from app.core.config import get_settings
from app.prompts.loaders import get_prompt
from app.llm.models import get_chat_model, get_fallback_model
from app.rag.vectorstore import get_vector_store
from app.tools.knowledge.handbook import file_search
from app.middleware.stacks import default_stack

# conn = sqlite3.connect(database="memory.db", check_name_thread=False)
# checkpointer = SqliteSaver(conn)

class ClauseAgent:
    def __init__(self) -> None:
        self.settings = get_settings() # instance attribute - composition - (RAGservices type Object) Composition - compulsory, Aggregation - optional
        self.store = get_vector_store(settings=self.settings)

        
        self.agent = create_agent(
        model=get_chat_model(settings=self.settings),
        tools=[file_search(store=self.store, top_k=self.settings.top_k)
        ],
        system_prompt=get_prompt(name="support/system", verison=self.settings.system_prompt_version),
        middleware=default_stack(settings=self.settings)
        # checkpointer=checkpointer
        
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
        self.store.client.close()




# print(response["response"][-1].text)