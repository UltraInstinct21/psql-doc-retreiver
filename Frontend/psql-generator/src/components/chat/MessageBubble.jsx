import { cn } from "@/lib/utils"
import { User } from "lucide-react"

export function MessageBubble({ children, className, ...props }) {
  return (
    <div
      data-slot="message-bubble"
      className={cn(
        "flex w-full items-start gap-3",
        className
      )}
      {...props}
    >
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted">
        <User className="size-4 text-muted-foreground" />
      </div>
      <div className="flex min-w-0 flex-1 flex-col">
        <div
          className={cn(
            "inline-block max-w-[640px] rounded-2xl bg-[#f5f5f7] px-4 py-3 text-[15px] leading-[1.5] text-[#1d1d1f] dark:bg-[#2a2a2c] dark:text-[#f5f5f7]"
          )}
        >
          {children}
        </div>
      </div>
    </div>
  )
}
