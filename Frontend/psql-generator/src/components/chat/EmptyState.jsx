import { cn } from "@/lib/utils"
import { Sparkles } from "lucide-react"

const defaultHints = [
  "Show all customers from last month",
  "Find duplicate email addresses",
  "Join orders with payments",
  "Monthly revenue aggregation",
]

export function EmptyState({ className, onSuggestionSelect, hints = defaultHints, ...props }) {
  return (
    <div
      data-slot="empty-state"
      className={cn(
        "flex flex-1 flex-col items-center justify-center py-24 text-center",
        className
      )}
      {...props}
    >
      <div className="mb-6 flex size-12 items-center justify-center rounded-full bg-primary/5">
        <Sparkles className="size-5 text-primary/40" />
      </div>
      <h2 className="text-[21px] font-semibold tracking-[0.231px] text-ink">
        AI PostgreSQL Query Assistant
      </h2>
      <p className="mt-2 max-w-md text-[14px] leading-[1.6] text-muted-foreground">
        Describe the query you need in natural language. The assistant rewrites your intent
        into retrieval-optimized queries, grounds the response in PostgreSQL documentation,
        and generates production-ready SQL.
      </p>
      <div className="mt-8 flex flex-wrap justify-center gap-2">
        {hints.map((hint) => (
          <button
            key={hint}
            onClick={() => onSuggestionSelect?.(hint)}
            className="rounded-full border border-border/50 bg-muted/20 px-3 py-1.5 text-[12px] text-muted-foreground/70 transition-colors hover:border-border hover:text-foreground"
          >
            {hint}
          </button>
        ))}
      </div>
    </div>
  )
}
