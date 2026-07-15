import { useEffect, useMemo, useState } from "react"
import { SubNav } from "@/components/layout/SubNav"
import { ChatTimeline } from "@/components/chat/ChatTimeline"
import { InputComposer } from "@/components/chat/InputComposer"
import { createRagClient, DEFAULT_API_BASE_URL } from "@/lib/api"
import { X, Clock, Trash2, Check } from "lucide-react"
import { cn } from "@/lib/utils"

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
  return new Date(timestamp).toLocaleString([], {
    hour: "2-digit",
    minute: "2-digit",
    month: "short",
    day: "numeric",
  })
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
    return () => { cancelled = true }
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
    <div className="flex min-h-svh flex-col bg-cocoa-black">
      <SubNav
        onHistoryClick={() => setHistoryOpen((current) => !current)}
        onSettingsClick={() => setSettingsOpen((current) => !current)}
      />
      <main className="flex flex-1 flex-col pt-13">
        <ChatTimeline
          className="flex-1 min-h-0"
          messages={messages}
          isLoading={isSending}
          onSuggestionSelect={sendQuery}
        />
        <InputComposer
          retrievalEnabled={retrievalEnabled}
          onRetrievalToggle={setRetrievalEnabled}
          onSend={sendQuery}
          isSending={isSending}
        />
      </main>

      {/* ─── History Panel ─── */}
      {historyOpen && (
        <div className="fixed inset-x-0 top-13 bottom-0 z-40 w-full sm:right-0 sm:left-auto sm:w-full sm:max-w-sm border-l border-warm-sand/10 bg-cocoa-black/95 backdrop-blur-2xl">
          <div className="flex items-center justify-between border-b border-warm-sand/10 px-5 py-4">
            <div className="min-w-0">
              <h3 className="text-[15px] font-medium text-cream-mist">History</h3>
              <p className="text-[12px] text-stone/60">Recent queries from this browser</p>
            </div>
            <button
              onClick={() => setHistoryOpen(false)}
              className="flex size-8 shrink-0 items-center justify-center rounded-pill text-stone/60 hover:text-cream-mist hover:bg-deep-plum/60 transition-colors"
              aria-label="Close history"
            >
              <X className="size-4" />
            </button>
          </div>

          <div className="flex items-center justify-between px-5 py-3 text-[12px]">
            <span className="text-stone/60">{history.length} queries saved</span>
            <button
              onClick={clearChat}
              className="inline-flex items-center gap-1 text-stone/60 hover:text-cream-mist transition-colors"
            >
              <Trash2 className="size-3" />
              Clear chat
            </button>
          </div>

          <div className="space-y-2 overflow-y-auto px-5 pb-5">
            {history.length === 0 ? (
              <div className="rounded-[8px] border border-dashed border-warm-sand/10 bg-deep-plum/30 p-5 text-center">
                <Clock className="mx-auto size-5 text-stone/40 mb-2" />
                <p className="text-[13px] text-stone/60">
                  No history yet. Send a question to start building a reusable query log.
                </p>
              </div>
            ) : (
              history.map((item) => (
                <button
                  key={item.id}
                  onClick={() => replayHistory(item)}
                  className="w-full rounded-[8px] border border-warm-sand/10 bg-deep-plum/40 p-3 text-left transition-all hover:bg-deep-plum/70 hover:border-warm-sand/20 active:bg-deep-plum"
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="truncate text-[13px] font-medium text-cream-mist/90">
                      {item.query}
                    </span>
                    <span className="shrink-0 text-[11px] text-stone/50">
                      {formatTime(item.timestamp)}
                    </span>
                  </div>
                  <div className="mt-1.5 flex items-center justify-between gap-2 text-[11px] text-stone/50">
                    <span className="truncate">{item.rewrite || "No rewrite cached"}</span>
                    <span className="shrink-0">{item.chunks} chunks</span>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}

      {/* ─── Settings Panel ─── */}
      {settingsOpen && (
        <div className="fixed inset-x-0 top-13 bottom-0 z-40 w-full sm:right-0 sm:left-auto sm:w-full sm:max-w-sm border-l border-warm-sand/10 bg-cocoa-black/95 backdrop-blur-2xl">
          <div className="flex items-center justify-between border-b border-warm-sand/10 px-5 py-4">
            <div className="min-w-0">
              <h3 className="text-[15px] font-medium text-cream-mist">Settings</h3>
              <p className="text-[12px] text-stone/60">Backend and retrieval controls</p>
            </div>
            <button
              onClick={() => setSettingsOpen(false)}
              className="flex size-8 shrink-0 items-center justify-center rounded-pill text-stone/60 hover:text-cream-mist hover:bg-deep-plum/60 transition-colors"
              aria-label="Close settings"
            >
              <X className="size-4" />
            </button>
          </div>

          <div className="space-y-5 px-5 py-5">
            {/* API URL */}
            <label className="block space-y-1.5">
              <span className="text-[11px] font-medium tracking-[0.06em] uppercase text-stone/60">
                API Base URL
              </span>
              <input
                value={settings.apiBaseUrl}
                onChange={(e) =>
                  setSettings((current) => ({ ...current, apiBaseUrl: e.target.value }))
                }
                className="w-full rounded-sm border border-warm-sand/15 bg-deep-plum/60 px-3 py-2.5 text-[13px] text-cream-mist outline-none placeholder:text-stone/40 transition-colors focus:border-mint-keyhole/40 focus:ring-1 focus:ring-mint-keyhole/20"
              />
            </label>

            {/* Top K */}
            <label className="block space-y-1.5">
              <span className="text-[11px] font-medium tracking-[0.06em] uppercase text-stone/60">
                Top K
              </span>
              <input
                type="number"
                min="1"
                max="20"
                value={settings.topK}
                onChange={(e) =>
                  setSettings((current) => ({ ...current, topK: Number(e.target.value) || 5 }))
                }
                className="w-full rounded-sm border border-warm-sand/15 bg-deep-plum/60 px-3 py-2.5 text-[13px] text-cream-mist outline-none transition-colors focus:border-mint-keyhole/40 focus:ring-1 focus:ring-mint-keyhole/20"
              />
            </label>

            {/* Default retrieval toggle */}
            <button
              onClick={() => {
                const next = !settings.defaultRetrievalEnabled
                setSettings((current) => ({ ...current, defaultRetrievalEnabled: next }))
                setRetrievalEnabled(next)
              }}
              className="flex w-full items-center justify-between rounded-sm border border-warm-sand/15 bg-deep-plum/60 px-3 py-2.5 text-[13px] text-left text-cream-mist transition-colors hover:bg-deep-plum"
            >
              <span className="font-medium">Default retrieval</span>
              <span
                className={cn(
                  "inline-flex items-center gap-1.5 text-[12px]",
                  settings.defaultRetrievalEnabled
                    ? "text-mint-keyhole"
                    : "text-stone/50"
                )}
              >
                {settings.defaultRetrievalEnabled ? (
                  <><Check className="size-3" /> On</>
                ) : (
                  "Off"
                )}
              </span>
            </button>

            {/* Backend status */}
            <div className="flex items-center justify-between rounded-sm border border-warm-sand/10 bg-deep-plum/40 px-3 py-2.5 text-[12px]">
              <span className="text-stone/60">Backend status</span>
              <span
                className={cn(
                  "font-medium",
                  apiStatus === "online"
                    ? "text-mint-keyhole"
                    : apiStatus === "offline"
                      ? "text-destructive"
                      : "text-stone/50"
                )}
              >
                {apiStatus}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* ─── Error Toast ─── */}
      {error && (
        <div className="fixed bottom-36 left-1/2 z-50 -translate-x-1/2">
          <div className="rounded-pill bg-aubergine px-5 py-2.5 text-[13px] font-medium text-cream-mist ring-1 ring-warm-sand/15 shadow-lg">
            {error}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
