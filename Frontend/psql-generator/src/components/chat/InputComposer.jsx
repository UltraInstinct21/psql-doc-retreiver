import { useState, useRef, useEffect } from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Database, ArrowUp } from "lucide-react"

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
        "fixed bottom-0 right-0 left-0 z-30 border-t border-border/30 bg-canvas/90 backdrop-blur-2xl",
        className
      )}
      style={{ backdropFilter: "saturate(180%) blur(20px)" }}
      {...props}
    >
      <div className="mx-auto flex w-full max-w-[768px] flex-col gap-2 px-4 py-3">
        <div className="relative flex items-end gap-2">
          <div className="relative flex-1">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a PostgreSQL question..."
              className="min-h-[44px] rounded-2xl border-border/50 bg-muted/30 px-4 py-3 pr-12 text-[15px] leading-[1.5] placeholder:text-muted-foreground/40 focus-visible:border-ring/30 focus-visible:ring-2 focus-visible:ring-ring/10"
              rows={1}
            />
            <Button
              size="icon"
              variant="ghost"
              onClick={handleSend}
              disabled={!input.trim() || isSending}
              className="absolute right-1.5 bottom-1.5 size-8 rounded-full text-muted-foreground hover:text-foreground disabled:opacity-30"
            >
              <ArrowUp className="size-4" />
            </Button>
          </div>
        </div>
        <div className="flex items-center justify-between px-1">
          <button
            onClick={() => onRetrievalToggle?.(!retrievalEnabled)}
            className={cn(
              "flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium tracking-wide transition-colors",
              retrievalEnabled
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground/50 hover:text-muted-foreground/70"
            )}
          >
            <Database className="size-3" />
            Retrieval
          </button>
          <span className="text-[10px] text-muted-foreground/30">
            <kbd className="rounded border border-border/30 px-1 py-0.5 text-[9px]">⌘</kbd>
            <kbd className="ml-0.5 rounded border border-border/30 px-1 py-0.5 text-[9px]">↵</kbd>
            {" "}to send
          </span>
        </div>
      </div>
    </div>
  )
}
