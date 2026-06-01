import { cn } from "@/lib/utils"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MessageBubble } from "@/components/chat/MessageBubble"
import { RewritePreview } from "@/components/chat/RewritePreview"
import { AssistantMessage } from "@/components/chat/AssistantMessage"
import { RetrievalPanel } from "@/components/chat/RetrievalPanel"
import { EmptyState } from "@/components/chat/EmptyState"

export function ChatTimeline({ messages = [], isLoading = false, loadingLabel = "Thinking…", onSuggestionSelect, className, ...props }) {
  const hasMessages = messages.length > 0

  return (
    <ScrollArea
      data-slot="chat-timeline"
      className={cn("h-full w-full", className)}
      {...props}
    >
      <div className="mx-auto flex w-full max-w-[768px] flex-col gap-6 px-4 py-6">
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
                {msg.chunks && <RetrievalPanel chunks={msg.chunks} />}
              </>
            )}

            {msg.type === "loading" && (
              <MessageBubble>{msg.content || loadingLabel}</MessageBubble>
            )}
          </div>
        ))}

        {isLoading && !messages.some((msg) => msg.type === "loading") && (
          <MessageBubble>{loadingLabel}</MessageBubble>
        )}
      </div>
    </ScrollArea>
  )
}
