const DEFAULT_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"

async function request(baseUrl, path, body) {
  const response = await fetch(`${baseUrl}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed with status ${response.status}`)
  }

  return response.json()
}

async function getJson(baseUrl, path) {
  const response = await fetch(`${baseUrl}${path}`)

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed with status ${response.status}`)
  }

  return response.json()
}

export function createRagClient(baseUrl = DEFAULT_API_BASE_URL) {
  return {
    baseUrl,
    chat: (payload) => request(baseUrl, "/chat", payload),
    rewrite: (query) => request(baseUrl, "/rewrite", { query }),
    retrieval: (query, topK) => request(baseUrl, "/retrieval", { query, top_k: topK }),
    health: () => getJson(baseUrl, "/health"),
  }
}

export { DEFAULT_API_BASE_URL }
