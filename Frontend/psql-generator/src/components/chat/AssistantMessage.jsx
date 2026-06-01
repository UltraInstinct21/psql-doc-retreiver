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
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
        <Sparkles className="size-4 text-primary" />
      </div>
      <div className="min-w-0 flex-1 space-y-3">
        <span className="text-[11px] font-medium tracking-wide text-muted-foreground/50 uppercase">
          Generated SQL
        </span>

        {sql && <SqlBlock sql={sql} />}

        {explanation && (
          <p className="max-w-[640px] text-[14px] leading-[1.6] text-muted-foreground">
            {explanation}
          </p>
        )}

        {optimizationNotes && (
          <div className="max-w-[640px] rounded-lg border border-border/50 bg-muted/30 px-3 py-2">
            <span className="text-[10px] font-semibold tracking-wide text-muted-foreground/60 uppercase">
              Optimization
            </span>
            <p className="mt-0.5 text-[13px] leading-[1.5] text-muted-foreground/80">
              {optimizationNotes}
            </p>
          </div>
        )}

        {assumptions && (
          <div className="max-w-[640px] rounded-lg border border-border/50 bg-muted/30 px-3 py-2">
            <span className="text-[10px] font-semibold tracking-wide text-muted-foreground/60 uppercase">
              Assumptions
            </span>
            <p className="mt-0.5 text-[13px] leading-[1.5] text-muted-foreground/80">
              {assumptions}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
