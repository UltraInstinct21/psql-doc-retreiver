import asyncio
import sys
from backend.app.services.rag_service import RAGService
from backend.app.core.config import settings

async def main():
    # Initialize RAGService directly from backend app
    rag = RAGService()
    await rag.initialize()

    print("\n💬 RAG Chat Ready (type 'exit' or 'quit' to quit)\n")
    if not settings.gemini_api_key:
        print("⚠️  GEMINI_API_KEY is missing. Answer generation is disabled.")

    history_turns = []

    while True:
        try:
            query = input("🔍 Question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if query.lower() in {"exit", "quit"}:
            break
        if not query:
            continue

        # Format history turns for the model
        history_str = "\n".join(history_turns)

        response = await rag.chat(query, history=history_str, retrieval_enabled=True)
        print(f"🔁 Rewrite intent: {response.rewrite.intent} | {response.rewrite.rewritten_query}")

        print("\n🧠 Answer:\n")
        if response.answer.sql:
            print(f"SQL:\n{response.answer.sql}\n")
        print(response.answer.explanation)
        if response.answer.optimization_notes:
            print(f"\nOptimization Notes:\n{response.answer.optimization_notes}")
        if response.answer.assumptions:
            print(f"\nAssumptions:\n{response.answer.assumptions}")

        print("\n📚 Top Documents (Reranked):\n")
        for i, chunk in enumerate(response.chunks, 1):
            print(f"--- Document {i} ---")
            print(f"Heading: {chunk.title} | Source: {chunk.source} | Rerank Score: {chunk.score:.4f}")
            print(f"Content:\n{chunk.content}")
            print()

        # Update conversation history with the new turn
        history_turns.append(f"User: {query}")
        history_turns.append(f"Assistant: {response.answer.explanation}")

        # Keep a rolling window of history (e.g., last 5 turns)
        if len(history_turns) > 10:
            history_turns = history_turns[-10:]

        print("=" * 60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())