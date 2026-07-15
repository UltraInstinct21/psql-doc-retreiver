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
      {/* User avatar — deep plum circle */}
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-deep-plum ring-1 ring-warm-sand/10">
        <User className="size-4 text-stone" />
      </div>

      <div className="min-w-0 flex-1">
        <div className="inline-block max-w-full sm:max-w-[640px] rounded-[8px] bg-deep-plum px-4 py-3 text-[15px] leading-[1.6] text-cream-mist ring-1 ring-warm-sand/10">
          {children}
        </div>
      </div>
    </div>
  )
}
