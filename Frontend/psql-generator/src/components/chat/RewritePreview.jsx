import { cn } from "@/lib/utils"
import { RefreshCw } from "lucide-react"

export function RewritePreview({ rewrite, className, ...props }) {
  if (!rewrite) return null

  const rewrittenQuery = typeof rewrite === "string" ? rewrite : rewrite.rewritten_query
  const intent = typeof rewrite === "string" ? null : rewrite.intent
  const searchQueries = typeof rewrite === "string" ? [] : rewrite.search_queries || []

  return (
    <div
      data-slot="rewrite-preview"
      className={cn(
        "ml-0 sm:ml-11 animate-in fade-in slide-in-from-top-1 duration-300",
        className
      )}
      {...props}
    >
      {/* Iris left-accent border */}
      <div className="border-l-2 border-iris/30 pl-4 space-y-2">
        <div className="flex items-center gap-2">
          <RefreshCw className="size-3 text-iris/60" />
          <span className="text-[11px] font-medium tracking-[0.06em] uppercase text-iris/60">Query Rewrite</span>
        </div>

        <p className="text-[13px] leading-[1.5] text-cream-mist/60 font-mono">
          {rewrittenQuery}
        </p>

        {intent && (
          <p className="text-[11px] tracking-[0.06em] uppercase text-stone/45">
            Intent: {intent.replace(/_/g, " ")}
          </p>
        )}

        {searchQueries.length > 1 && (
          <div className="flex flex-wrap gap-2 pt-1">
            {searchQueries.map((query, index) => (
              <span
                key={`${query}-${index}`}
                className="rounded-pill border border-warm-sand/10 bg-deep-plum/60 px-2.5 py-1 text-[11px] font-medium text-stone/70"
              >
                {query}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
