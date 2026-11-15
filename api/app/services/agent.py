
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import HumanMessage

from app.services.chat import RAGService

SYSTEM = "You are helpful Clause AI Assistant!"

class ClauseAgent:
    def __init__(self) -> None:
        self.rag = RAGService()  # instance attribute - composition - (RAGservices type Object) Composition - compulsory, Aggregation - optional
        
        @tool(response_format="content_and_artifact")
        def search_handbook(query: str) -> None:
            """..."""
            pass

        self.agent = create_agent(
        model=self.rag.llm,
        tools=[search_handbook],
        system_prompt=SYSTEM
        
        )

    def ask(self) -> None:
        pass

    def close(self) -> None:
        self.rag.close()




# query = input("Query: ")
# # messages = [
# #     {"role": "user", "content": query}
# # ]

# response = agent.invoke({"messages":[HumanMessage(content=query)]})
# print(response["response"][-1].text)