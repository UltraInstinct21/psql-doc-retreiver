import { cn } from "@/lib/utils"
import { ChevronDown, FileText } from "lucide-react"

const sampleChunks = [
  { title: "2.5 Querying a Table", score: 0.975, snippet: "SELECT * FROM weather;\nSELECT city, temp_lo, temp_hi FROM weather;", source: "The SQL Language" },
  { title: "2.6 Joins Between Tables", score: 0.891, snippet: "SELECT * FROM weather JOIN cities ON weather.city = cities.name;", source: "The SQL Language" },
  { title: "7.2.1 Aggregate Functions", score: 0.764, snippet: "SELECT COUNT(*), AVG(temp_lo) FROM weather;", source: "Functions and Operators" },
]

function ChunkCard({ chunk }) {
  const scoreColor =
    chunk.score > 0.9
      ? "text-mint-keyhole"
      : chunk.score > 0.8
        ? "text-iris/80"
        : "text-stone/50"

  return (
    <div className="rounded-[8px] bg-cocoa-black/60 px-4 py-3 ring-1 ring-warm-sand/8">
      {/* Title + Score */}
      <div className="flex items-center justify-between gap-3">
        <span className="text-[13px] font-medium text-cream-mist/80 truncate">
          {chunk.title}
        </span>
        <span className={cn("shrink-0 text-[11px] font-mono font-medium", scoreColor)}>
          {chunk.score.toFixed(3)}
        </span>
      </div>

      {/* Source */}
      <span className="text-[11px] text-stone/50">{chunk.source}</span>

      {/* Snippet */}
      <pre className="mt-2 overflow-x-auto rounded-[4px] bg-cocoa-black/60 p-3 text-[11px] leading-[1.5] text-cream-mist/50 font-mono ring-1 ring-warm-sand/5">
        {chunk.snippet}
      </pre>
    </div>
  )
}

export function RetrievalPanel({ chunks = sampleChunks, className, ...props }) {
  return (
    <div
      data-slot="retrieval-panel"
      className={cn("ml-0 sm:ml-11 space-y-3", className)}
      {...props}
    >
      {/* Accordion-style toggle */}
      <details className="group">
        <summary className="flex cursor-pointer items-center gap-2 text-[11px] font-medium tracking-[0.06em] uppercase text-stone/50 hover:text-stone/80 list-none">
          <ChevronDown className="size-3 text-stone/40 transition-transform group-open:rotate-180" />
          <FileText className="size-3 text-stone/40" />
          <span>Retrieval Inspector ({chunks.length} chunks)</span>
        </summary>

        <div className="mt-3 space-y-2">
          {chunks.map((chunk, i) => (
            <ChunkCard key={i} chunk={chunk} />
          ))}
        </div>
      </details>
    </div>
  )
}
