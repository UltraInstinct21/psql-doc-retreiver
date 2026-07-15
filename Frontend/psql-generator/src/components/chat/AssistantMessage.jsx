import { cn } from "@/lib/utils"
import { Sparkles } from "lucide-react"
import { SqlBlock } from "@/components/chat/SqlBlock"

export function AssistantMessage({
  sql,
  explanation,
  assumptions,
  optimizationNotes,
  className,
  ...props
}) {
  return (
    <div
      data-slot="assistant-message"
      className={cn("flex w-full items-start gap-3", className)}
      {...props}
    >
      {/* AI avatar — mint keyhole glow */}
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-mint-keyhole/10 ring-1 ring-mint-keyhole/20">
        <Sparkles className="size-4 text-mint-keyhole" />
      </div>

      {/* Content */}
      <div className="min-w-0 flex-1 space-y-4">
        {/* SQL block */}
        {sql && (
          <div className="space-y-2">
            <SqlBlock sql={sql} />
          </div>
        )}

        {/* Explanation */}
        {explanation && (
          <div className="max-w-full sm:max-w-[640px]">
            <span className="text-[11px] font-medium tracking-[0.06em] uppercase text-stone/50">Explanation</span>
            <p className="mt-1.5 text-[14px] leading-[1.6] text-cream-mist/80">
              {explanation}
            </p>
          </div>
        )}

        {/* Optimization notes — plum card with iris accent */}
        {optimizationNotes && (
          <div className="max-w-full sm:max-w-[640px] rounded-[8px] bg-deep-plum px-4 py-3 ring-1 ring-warm-sand/10">
            <div className="flex items-center gap-2 mb-1.5">
              <div className="h-3 w-0.5 rounded-full bg-iris/60" />
              <span className="text-[10px] font-medium tracking-[0.06em] uppercase text-iris/70">Optimization</span>
            </div>
            <p className="text-[13px] leading-[1.5] text-cream-mist/70">
              {optimizationNotes}
            </p>
          </div>
        )}

        {/* Assumptions — plum card with warm border */}
        {assumptions && (
          <div className="max-w-full sm:max-w-[640px] rounded-[8px] bg-deep-plum px-4 py-3 ring-1 ring-warm-sand/10">
            <div className="flex items-center gap-2 mb-1.5">
              <div className="h-3 w-0.5 rounded-full bg-stone/40" />
              <span className="text-[10px] font-medium tracking-[0.06em] uppercase text-stone/50">Assumptions</span>
            </div>
            <p className="text-[13px] leading-[1.5] text-cream-mist/70">
              {assumptions}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
