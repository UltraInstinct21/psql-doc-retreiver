import { useState, useRef, useEffect } from "react"
import { cn } from "@/lib/utils"
import { ArrowUp, Database } from "lucide-react"

export function InputComposer({
  onSend,
  retrievalEnabled,
  onRetrievalToggle,
  isSending,
  className,
  ...props
}) {
  const [input, setInput] = useState("")
  const textareaRef = useRef(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 160) + "px"
    }
  }, [input])

  const handleSend = () => {
    if (!input.trim() || isSending) return
    onSend?.(input.trim())
    setInput("")
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div
      data-slot="input-composer"
      className={cn(
        "border-t border-warm-sand/8 bg-cocoa-black",
        className
      )}
      {...props}
    >
      <div className="mx-auto flex w-full max-w-[768px] flex-col gap-2 px-3 sm:px-4 py-3 sm:py-4">
        {/* Input row */}
        <div className="relative flex items-end gap-2">
          <div className="relative flex-1">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a PostgreSQL question..."
              className="min-h-[48px] max-h-[160px] w-full resize-none rounded-[8px] border border-warm-sand/15 bg-deep-plum/60 px-4 py-3 pr-14 text-[15px] leading-[1.5] text-cream-mist placeholder:text-stone/40 font-medium outline-none transition-colors focus:border-mint-keyhole/40 focus:ring-1 focus:ring-mint-keyhole/20"
              rows={1}
            />
            {/* Send button — mint filled pill */}
            <button
              onClick={handleSend}
              disabled={!input.trim() || isSending}
              className="absolute right-2 bottom-2 flex size-9 items-center justify-center rounded-pill bg-mint-keyhole text-cocoa-black transition-all hover:bg-mint-keyhole/90 disabled:opacity-30 disabled:cursor-not-allowed active:scale-95"
            >
              <ArrowUp className="size-4" />
            </button>
          </div>
        </div>

        {/* Footer row */}
        <div className="flex items-center justify-between px-1">
          {/* Retrieval toggle */}
          <button
            onClick={() => onRetrievalToggle?.(!retrievalEnabled)}
            className={cn(
              "inline-flex items-center gap-1.5 rounded-pill px-3 py-1.5 text-[11px] font-medium tracking-[0.02em] transition-colors",
              retrievalEnabled
                ? "bg-mint-keyhole/10 text-mint-keyhole ring-1 ring-mint-keyhole/20"
                : "text-stone/50 hover:text-stone/70"
            )}
          >
            <Database className="size-3" />
            Retrieval
          </button>

          {/* Keyboard hint */}
          <span className="hidden sm:inline text-[10px] text-stone/30">
            <kbd className="rounded-[4px] border border-warm-sand/15 px-1.5 py-0.5 text-[9px] font-mono text-stone/40">
              ⌘
            </kbd>
            <kbd className="ml-0.5 rounded-[4px] border border-warm-sand/15 px-1.5 py-0.5 text-[9px] font-mono text-stone/40">
              ↵
            </kbd>
            {" "}
            <span className="text-stone/30">to send</span>
          </span>
        </div>
      </div>
    </div>
  )
}
