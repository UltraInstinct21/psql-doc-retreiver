import { cn } from "@/lib/utils"

export function RewritePreview({ rewrite, className, ...props }) {
  if (!rewrite) return null

  const rewrittenQuery = typeof rewrite === "string" ? rewrite : rewrite.rewritten_query
  const intent = typeof rewrite === "string" ? null : rewrite.intent
  const searchQueries = typeof rewrite === "string" ? [] : rewrite.search_queries || []

  return (
    <div
      data-slot="rewrite-preview"
      className={cn(
        "ml-11 animate-in fade-in slide-in-from-top-1 duration-300",
        className
      )}
      {...props}
    >
      <div className="border-l-2 border-muted-foreground/20 pl-4">
        <span className="text-[11px] font-medium tracking-wide text-muted-foreground/50 uppercase">
          Query Rewrite
        </span>
        <p className="mt-1 text-[13px] leading-[1.5] text-muted-foreground/70 font-mono">
          {rewrittenQuery}
        </p>
        {intent && (
          <p className="mt-2 text-[11px] uppercase tracking-wide text-muted-foreground/45">
            Intent: {intent.replace(/_/g, " ")}
          </p>
        )}
        {searchQueries.length > 1 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {searchQueries.map((query, index) => (
              <span
                key={`${query}-${index}`}
                className="rounded-full border border-border/40 bg-muted/20 px-2 py-1 text-[11px] text-muted-foreground/70"
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
