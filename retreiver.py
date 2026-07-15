import asyncio
import sys
from backend.app.services.rag_service import RAGService
from backend.app.core.config import settings

async def main():
    # Initialize RAGService directly from backend app
    rag = RAGService()
    await rag.initialize()

    print("\n🔍 Retriever Ready (type 'exit' or 'quit' to quit)")
    if not settings.gemini_api_key:
        print("⚠️  GEMINI_API_KEY is missing. Answer generation is disabled.")

    while True:
        try:
            query = input("\n🔍 Enter your query: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if query.lower() in {"exit", "quit"}:
            break
        if not query:
            continue

        response = await rag.chat(query, retrieval_enabled=True)
        print(f"🔁 Rewrite: {response.rewrite.rewritten_query}")

        print("\n📄 Top Results:\n" + "-" * 50)
        for i, chunk in enumerate(response.chunks, 1):
            print(f"\nResult {i}")
            print(f"Source: {chunk.source} | Score: {chunk.score:.4f}")
            print(f"Heading: {chunk.title}")
            # Print first 500 chars of content (similar to original)
            print("Content:\n", chunk.content[:500])

        if settings.gemini_api_key:
            print("\n🧠 Gemini Answer:\n")
            if response.answer.sql:
                print(f"SQL:\n{response.answer.sql}\n")
            print(response.answer.explanation)
            if response.answer.optimization_notes:
                print(f"\nOptimization Notes:\n{response.answer.optimization_notes}")
            if response.answer.assumptions:
                print(f"\nAssumptions:\n{response.answer.assumptions}")

        print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())