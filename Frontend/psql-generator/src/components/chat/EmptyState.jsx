import { cn } from "@/lib/utils"
import { Database, Sparkles } from "lucide-react"

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
        "flex min-h-0 flex-1 flex-col items-center justify-center gap-8 py-16 sm:py-24 px-4",
        className
      )}
      {...props}
    >
      {/* Mint keyhole icon */}
      <div className="relative">
        <div className="flex size-14 shrink-0 items-center justify-center rounded-full bg-mint-keyhole/10 ring-1 ring-mint-keyhole/20">
          <Database className="size-6 text-mint-keyhole" />
        </div>
        <div className="absolute -inset-2 rounded-full bg-mint-keyhole/5 blur-xl" />
      </div>

      {/* Headline — "First Word Mint" rule */}
      <div className="w-full max-w-lg space-y-3 text-center">
        <h2 className="text-[28px] font-light leading-[1.2] tracking-[0.28px] text-cream-mist">
          <span className="text-mint-keyhole">PostgreSQL</span> Query Assistant
        </h2>
        <p className="mx-auto max-w-[55ch] text-[15px] leading-[1.6] text-stone">
          Describe the query you need in natural language. The assistant rewrites your intent
          into retrieval-optimized queries, grounds the response in PostgreSQL documentation,
          and generates production-ready SQL.
        </p>
      </div>

      {/* Hint pills */}
      <div className="w-full overflow-x-auto">
        <div className="flex w-max items-center gap-2 mx-auto px-1">
          {hints.map((hint) => (
            <button
              key={hint}
              onClick={() => onSuggestionSelect?.(hint)}
              className="whitespace-nowrap rounded-pill border border-warm-sand/15 bg-deep-plum/50 px-4 py-2 text-[13px] font-medium text-stone transition-all hover:border-mint-keyhole/30 hover:text-cream-mist hover:bg-deep-plum active:scale-[0.97]"
            >
              {hint}
            </button>
          ))}
        </div>
      </div>

      {/* Subdued hint */}
      <p className="text-[11px] tracking-[0.06em] uppercase text-stone/50">
        Ask anything about PostgreSQL
      </p>
    </div>
  )
}
