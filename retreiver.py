import asyncio
import json
import os
import re

from dotenv import load_dotenv

from langchain_postgres import PGEngine, PGVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sentence_transformers import CrossEncoder

load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------
POSTGRES_USER = "sarthi"
POSTGRES_PASSWORD = "2106"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "rag_db"

TABLE_NAME = "pg_docs_topicwise"
TOP_K = 5
RETRIEVAL_K = TOP_K * 4
HYBRID_SEMANTIC_WEIGHT = 0.7
HYBRID_KEYWORD_WEIGHT = 0.3
RERANKER_DEVICE = os.getenv("RERANKER_DEVICE", "cpu")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
QUERY_REWRITE_LIMIT = 3

RETRIEVER_USE_GEMINI = os.getenv("RETRIEVER_USE_GEMINI", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

CONNECTION_STRING = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# -----------------------------
# EMBEDDING MODEL (same as ingest)
# -----------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-en-v1.5",
    model_kwargs={"device": "cuda"},
    encode_kwargs={"normalize_embeddings": True},
)


def _pick_reranker_device() -> str:
    if RERANKER_DEVICE == "auto":
        return "cpu"
    return RERANKER_DEVICE


reranker_device = _pick_reranker_device()
reranker = CrossEncoder(
    "BAAI/bge-reranker-large",
    max_length=512,
    device=reranker_device,
    trust_remote_code=True,
    cache_folder=os.path.expanduser("~/.cache/huggingface"),
)

# -----------------------------
# QUERY REWRITER
# -----------------------------
def _build_rewriter_chain():
    rewriter_prompt = ChatPromptTemplate.from_messages([
        ("system",
"""
You are QueryRewriteAgent for a PostgreSQL documentation RAG system.

Goal:
- Rewrite the user query for retrieval, not for answering.

Required output:
- Return JSON only.
- Use exactly these keys:
  - intent: one of [sql_syntax, definition, how_to, debugging, conceptual, api_lookup, configuration]
  - rewritten_query: a single canonical retrieval query
  - search_queries: 2 to 3 short retrieval queries ordered by usefulness
  - rerank_query: the best single query for cross-encoder reranking
  - entities: object with keys table_name, function_name, api, class_name, library_name
  - difficulty: one of [beginner, intermediate, advanced]

Rewrite rules:
- Normalize casual wording into technical terms.
- Do not invent facts, schema, or APIs not in the user query.
- Do not add explanation text, markdown, or code fences.
"""),
        ("user", "Rewrite this query for retrieval:\n{query}\n\nReturn JSON only."),
    ])
    return rewriter_prompt | _build_llm(GEMINI_MODEL) | StrOutputParser()


def rewrite_query(query: str) -> dict:
    if not GEMINI_API_KEY:
        return {
            "intent": "conceptual",
            "rewritten_query": query,
            "search_queries": [query],
            "rerank_query": query,
            "entities": {},
            "difficulty": "intermediate",
        }

    rewriter_chain = _build_rewriter_chain()
    raw = rewriter_chain.invoke({"query": query})
    try:
        plan = json.loads(raw)
    except Exception:
        plan = {}

    search_queries = plan.get("search_queries") or [plan.get("rewritten_query", query)]
    if isinstance(search_queries, str):
        search_queries = [search_queries]
    search_queries = [str(item).strip() for item in search_queries if str(item).strip()]
    if query not in search_queries:
        search_queries.insert(0, query)
    search_queries = search_queries[:QUERY_REWRITE_LIMIT]

    return {
        "intent": plan.get("intent", "conceptual"),
        "rewritten_query": plan.get("rewritten_query", query),
        "search_queries": search_queries,
        "rerank_query": plan.get("rerank_query", plan.get("rewritten_query", query)),
        "entities": plan.get("entities", {}),
        "difficulty": plan.get("difficulty", "intermediate"),
    }


# -----------------------------
# OPTIONAL GEMINI QA CHAIN
# -----------------------------
qa_chain = None
if RETRIEVER_USE_GEMINI and GEMINI_API_KEY:
    llm = _build_llm(GEMINI_MODEL)

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a PostgreSQL expert assistant. Answer using only provided context."),
        ("user", "QUESTION:\n{question}\n\nREWRITE:\n{rewrite}\n\nCONTEXT:\n{context}\n\nANSWER:"),
    ])

    qa_chain = qa_prompt | llm | StrOutputParser()

# -----------------------------
# MAIN RETRIEVER
# -----------------------------
def _query_terms(query: str) -> set[str]:
    return {word.lower() for word in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]+", query)}


def _hybrid_score(query_terms: set[str], doc) -> float:
    text = f"{doc.metadata.get('heading', '')} {doc.page_content}".lower()
    overlap = len(query_terms & set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]+", text)))
    keyword_score = min(1.0, overlap / max(1, len(query_terms)))
    return keyword_score


def _doc_identity(doc) -> str:
    meta = doc.metadata or {}
    return str(meta.get("chunk_id") or meta.get("heading") or doc.page_content[:120])


async def hybrid_retrieve(store, search_queries: list[str], rerank_query: str, top_k: int = TOP_K, candidate_k: int = RETRIEVAL_K):
    scored = {}
    for search_query in search_queries:
        try:
            pairs = await store.asimilarity_search_with_score(search_query, k=candidate_k)
            docs = [(doc, float(score), search_query) for doc, score in pairs]
        except Exception:
            docs = [(doc, float(i), search_query) for i, doc in enumerate(await store.asimilarity_search(search_query, k=candidate_k))]

        for doc, score, source_query in docs:
            ident = _doc_identity(doc)
            if ident not in scored or score < scored[ident][1]:
                scored[ident] = (doc, score, source_query)

    if not scored:
        return []

    query_terms = _query_terms(rerank_query)
    scored_list = list(scored.values())
    scored_list.sort(key=lambda item: item[1])
    total = max(1, len(scored_list) - 1)

    hybrid = []
    for rank, (doc, _, source_query) in enumerate(scored_list):
        semantic = 1.0 - (rank / total)
        keyword = _hybrid_score(query_terms, doc)
        query_bonus = 0.05 if source_query == search_queries[0] else 0.0
        hybrid.append((doc, HYBRID_SEMANTIC_WEIGHT * semantic + HYBRID_KEYWORD_WEIGHT * keyword + query_bonus))

    hybrid.sort(key=lambda item: item[1], reverse=True)
    docs = [doc for doc, _ in hybrid[:candidate_k]]

    if not docs:
        return []

    pairs = [(rerank_query, doc.page_content) for doc in docs]
    try:
        rerank_scores = reranker.predict(pairs)
        order = sorted(range(len(rerank_scores)), key=lambda i: rerank_scores[i], reverse=True)[:top_k]
        final_docs = [docs[i] for i in order]
        for i, idx in enumerate(order):
            final_docs[i].metadata["rerank_score"] = float(rerank_scores[idx])
        return final_docs
    except Exception:
        return docs[:top_k]


async def main():
    pg_engine = PGEngine.from_connection_string(CONNECTION_STRING)

    store = await PGVectorStore.create(
        engine=pg_engine,
        table_name=TABLE_NAME,
        embedding_service=embedding_model,
    )

    print("\n🔍 Retriever Ready (type 'exit' to quit)")
    if RETRIEVER_USE_GEMINI and not GEMINI_API_KEY:
        print("⚠️  RETRIEVER_USE_GEMINI is enabled but GEMINI_API_KEY is missing. QA mode disabled.")

    while True:
        query = input("\n🔍 Enter your query: ").strip()
        if query.lower() in {"exit", "quit"}:
            break
        if not query:
            continue

        query_plan = rewrite_query(query)
        print(f"🔁 Rewrite: {query_plan['rewritten_query']}")
        docs = await hybrid_retrieve(store, query_plan["search_queries"], query_plan["rerank_query"])

        print("\n📄 Top Results:\n" + "-" * 50)

        for i, doc in enumerate(docs, 1):
            print(f"\nResult {i}")
            print("Metadata:", doc.metadata)
            print("Content:\n", doc.page_content[:500])

        if qa_chain:
            context = "\n\n---\n\n".join(doc.page_content for doc in docs)
            rewrite_json = json.dumps(query_plan)
            answer = qa_chain.invoke({"question": query_plan["rewritten_query"], "rewrite": rewrite_json, "context": context})
            print("\n🧠 Gemini Answer:\n")
            print(answer)

        print("\n" + "=" * 60)


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())