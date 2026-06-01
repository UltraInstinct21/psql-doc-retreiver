import { useEffect, useMemo, useState } from "react"
import { SubNav } from "@/components/layout/SubNav"
import { ChatTimeline } from "@/components/chat/ChatTimeline"
import { InputComposer } from "@/components/chat/InputComposer"
import { createRagClient, DEFAULT_API_BASE_URL } from "@/lib/api"

const HISTORY_STORAGE_KEY = "psql-generator-history"
const SETTINGS_STORAGE_KEY = "psql-generator-settings"

function readJson(key, fallback) {
  if (typeof window === "undefined") return fallback
  try {
    const raw = window.localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch {
    return fallback
  }
}

function makeId(prefix) {
  if (window.crypto?.randomUUID) {
    return `${prefix}-${window.crypto.randomUUID()}`
  }

  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleString([], { hour: "2-digit", minute: "2-digit", month: "short", day: "numeric" })
}

export function App() {
  const [settings, setSettings] = useState(() =>
    readJson(SETTINGS_STORAGE_KEY, {
      apiBaseUrl: DEFAULT_API_BASE_URL,
      defaultRetrievalEnabled: true,
      topK: 5,
    })
  )
  const [messages, setMessages] = useState([])
  const [history, setHistory] = useState(() => readJson(HISTORY_STORAGE_KEY, []))
  const [retrievalEnabled, setRetrievalEnabled] = useState(settings.defaultRetrievalEnabled ?? true)
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState("")
  const [historyOpen, setHistoryOpen] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [apiStatus, setApiStatus] = useState("unknown")

  const client = useMemo(() => createRagClient(settings.apiBaseUrl), [settings.apiBaseUrl])

  useEffect(() => {
    window.localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(settings))
  }, [settings])

  useEffect(() => {
    window.localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history.slice(0, 20)))
  }, [history])

  useEffect(() => {
    let cancelled = false
    client
      .health()
      .then(() => {
        if (!cancelled) setApiStatus("online")
      })
      .catch(() => {
        if (!cancelled) setApiStatus("offline")
      })

    return () => {
      cancelled = true
    }
  }, [client])

  const sendQuery = async (query) => {
    const trimmed = query.trim()
    if (!trimmed || isSending) return

    const userMessage = { id: makeId("user"), type: "user", content: trimmed }
    setMessages((current) => [...current, userMessage])
    setError("")
    setIsSending(true)

    try {
      const response = await client.chat({
        query: trimmed,
        retrieval_enabled: retrievalEnabled,
        top_k: settings.topK,
      })

      const rewriteMessage = {
        id: makeId("rewrite"),
        type: "rewrite",
        rewrite: response.rewrite,
      }

      const assistantMessage = {
        id: makeId("assistant"),
        type: "assistant",
        sql: response.answer?.sql || "",
        explanation: response.answer?.explanation || "",
        optimizationNotes: response.answer?.optimization_notes || "",
        assumptions: response.answer?.assumptions || "",
        chunks: response.chunks || [],
      }

      setMessages((current) => [...current, rewriteMessage, assistantMessage])
      setHistory((current) => [
        {
          id: makeId("history"),
          query: trimmed,
          rewrite: response.rewrite?.rewritten_query || "",
          timestamp: Date.now(),
          chunks: response.chunks?.length || 0,
        },
        ...current,
      ])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed")
      setMessages((current) => [
        ...current,
        {
          id: makeId("assistant-error"),
          type: "assistant",
          sql: "",
          explanation: "The backend request failed. Check the API URL and server status.",
          optimizationNotes: "",
          assumptions: "",
          chunks: [],
        },
      ])
    } finally {
      setIsSending(false)
      setHistoryOpen(false)
    }
  }

  const replayHistory = (item) => {
    setHistoryOpen(false)
    sendQuery(item.query)
  }

  const clearChat = () => setMessages([])

  return (
    <div className="flex min-h-svh flex-col bg-background">
      <SubNav
        onHistoryClick={() => setHistoryOpen((current) => !current)}
        onSettingsClick={() => setSettingsOpen((current) => !current)}
      />
      <main className="flex flex-1 flex-col pt-13 pb-32">
        <ChatTimeline
          messages={messages}
          isLoading={isSending}
          onSuggestionSelect={sendQuery}
        />
      </main>
      <InputComposer
        retrievalEnabled={retrievalEnabled}
        onRetrievalToggle={setRetrievalEnabled}
        onSend={sendQuery}
        isSending={isSending}
      />

      {historyOpen && (
        <div className="fixed top-13 right-0 bottom-0 z-40 w-full max-w-sm border-l border-border/50 bg-background/95 backdrop-blur-xl">
          <div className="flex items-center justify-between border-b border-border/40 px-4 py-3">
            <div>
              <h3 className="text-[14px] font-semibold">History</h3>
              <p className="text-[12px] text-muted-foreground">Recent queries from this browser</p>
            </div>
            <button className="text-[12px] text-muted-foreground" onClick={() => setHistoryOpen(false)}>
              Close
            </button>
          </div>
          <div className="flex items-center justify-between px-4 py-3 text-[12px] text-muted-foreground">
            <span>{history.length} queries saved</span>
            <button className="text-primary" onClick={clearChat}>Clear chat</button>
          </div>
          <div className="space-y-2 overflow-y-auto px-4 pb-4">
            {history.length === 0 ? (
              <p className="rounded-lg border border-dashed border-border/50 p-4 text-[13px] text-muted-foreground">
                No history yet. Send a question to start building a reusable query log.
              </p>
            ) : (
              history.map((item) => (
                <button
                  key={item.id}
                  className="w-full rounded-lg border border-border/50 bg-muted/20 p-3 text-left transition-colors hover:bg-muted/40"
                  onClick={() => replayHistory(item)}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-[13px] font-medium">{item.query}</span>
                    <span className="text-[11px] text-muted-foreground">{formatTime(item.timestamp)}</span>
                  </div>
                  <div className="mt-1 flex items-center justify-between text-[11px] text-muted-foreground">
                    <span>{item.rewrite || "No rewrite cached"}</span>
                    <span>{item.chunks} chunks</span>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}

      {settingsOpen && (
        <div className="fixed top-13 right-0 bottom-0 z-40 w-full max-w-sm border-l border-border/50 bg-background/95 backdrop-blur-xl">
          <div className="border-b border-border/40 px-4 py-3">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-[14px] font-semibold">Settings</h3>
                <p className="text-[12px] text-muted-foreground">Backend and retrieval controls</p>
              </div>
              <button className="text-[12px] text-muted-foreground" onClick={() => setSettingsOpen(false)}>
                Close
              </button>
            </div>
          </div>
          <div className="space-y-4 px-4 py-4 text-[13px]">
            <label className="block space-y-1">
              <span className="text-[11px] uppercase tracking-wide text-muted-foreground">API base URL</span>
              <input
                value={settings.apiBaseUrl}
                onChange={(e) => setSettings((current) => ({ ...current, apiBaseUrl: e.target.value }))}
                className="w-full rounded-lg border border-border/50 bg-background px-3 py-2 text-[13px]"
              />
            </label>
            <label className="block space-y-1">
              <span className="text-[11px] uppercase tracking-wide text-muted-foreground">Top K</span>
              <input
                type="number"
                min="1"
                max="20"
                value={settings.topK}
                onChange={(e) => setSettings((current) => ({ ...current, topK: Number(e.target.value) || 5 }))}
                className="w-full rounded-lg border border-border/50 bg-background px-3 py-2 text-[13px]"
              />
            </label>
            <button
              className="flex w-full items-center justify-between rounded-lg border border-border/50 bg-muted/20 px-3 py-2 text-left"
              onClick={() => {
                const next = !settings.defaultRetrievalEnabled
                setSettings((current) => ({ ...current, defaultRetrievalEnabled: next }))
                setRetrievalEnabled(next)
              }}
            >
              <span>Default retrieval</span>
              <span className={settings.defaultRetrievalEnabled ? "text-primary" : "text-muted-foreground"}>
                {settings.defaultRetrievalEnabled ? "On" : "Off"}
              </span>
            </button>
            <div className="rounded-lg border border-border/50 bg-muted/20 px-3 py-2 text-[12px] text-muted-foreground">
              Backend status: <span className={apiStatus === "online" ? "text-green-600" : apiStatus === "offline" ? "text-red-600" : "text-muted-foreground"}>{apiStatus}</span>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="fixed bottom-36 left-1/2 z-50 -translate-x-1/2 rounded-full border border-destructive/30 bg-background px-4 py-2 text-[12px] text-destructive shadow-lg">
          {error}
        </div>
      )}
    </div>
  )
}

export default App
