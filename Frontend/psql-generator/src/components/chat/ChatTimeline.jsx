import { cn } from "@/lib/utils"
import { MessageBubble } from "@/components/chat/MessageBubble"
import { RewritePreview } from "@/components/chat/RewritePreview"
import { AssistantMessage } from "@/components/chat/AssistantMessage"
import { RetrievalPanel } from "@/components/chat/RetrievalPanel"
import { EmptyState } from "@/components/chat/EmptyState"
import { Loader } from "lucide-react"

export function ChatTimeline({
  messages = [],
  isLoading = false,
  loadingLabel = "Thinking…",
  onSuggestionSelect,
  className,
  ...props
}) {
  const hasMessages = messages.length > 0

  return (
    <div
      data-slot="chat-timeline"
      className={cn("w-full overflow-y-auto", className)}
      {...props}
    >
      <div className="mx-auto flex w-full max-w-[768px] flex-col gap-5 px-4 py-6">
        {!hasMessages && <EmptyState onSuggestionSelect={onSuggestionSelect} />}

        {messages.map((msg) => (
          <div key={msg.id} className="space-y-3">
            {msg.type === "user" && (
              <MessageBubble>{msg.content}</MessageBubble>
            )}

            {msg.type === "rewrite" && (
              <RewritePreview rewrite={msg.rewrite} />
            )}

            {msg.type === "assistant" && (
              <>
                <AssistantMessage
                  sql={msg.sql}
                  explanation={msg.explanation}
                  optimizationNotes={msg.optimizationNotes}
                  assumptions={msg.assumptions}
                />
                {msg.chunks?.length > 0 && (
                  <RetrievalPanel chunks={msg.chunks} />
                )}
              </>
            )}

            {msg.type === "loading" && (
              <MessageBubble>
                <div className="flex items-center gap-2">
                  <Loader className="size-3.5 animate-spin text-stone" />
                  <span>{msg.content || loadingLabel}</span>
                </div>
              </MessageBubble>
            )}
          </div>
        ))}

        {/* Persistent loading indicator when no loading message in list */}
        {isLoading && !messages.some((msg) => msg.type === "loading") && (
          <MessageBubble>
            <div className="flex items-center gap-2">
              <Loader className="size-3.5 animate-spin text-stone" />
              <span>{loadingLabel}</span>
            </div>
          </MessageBubble>
        )}
      </div>
    </div>
  )
}
