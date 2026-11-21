from app.services.agent import ClauseAgent

def main() -> None:
    clause_agent = ClauseAgent()
    try:
        thread_id = input("Conversation name: ")

        while True:
            query = input("You: ").strip()
            if not query:
                continue
            if query.lower() in {"quit", "bye", "exit"}:
                break
            
            result = clause_agent.ask(question=query, thread_id=thread_id)
            print(f"AI: {result['answer']}")

            for q in result["searches"]:
                print(f" searched : {q}")
            for s in result["sources"]:
                print(f"source: page {s['page']} (score {s['score']})")
   
    except (KeyboardInterrupt, EOFError):
        pass
   
    finally:
        clause_agent.close()


if __name__ == "__main__":
    main()
