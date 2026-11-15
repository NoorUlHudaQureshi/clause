from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.messages import HumanMessage



llm = init_chat_model(
    model="gemma3:1b",
    model_provider="ollama",
    temperature=0.1
)

agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="You are a helpful Clause Ai Assitant!"
)

query = input("Query: ")
# messages = [
#     {"role": "user", "content": query}
# ]

response = agent.invoke({"messages":[HumanMessage(content=query)]})
print(response["response"][-1].text)