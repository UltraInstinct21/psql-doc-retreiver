import { cn } from "@/lib/utils"
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion"

const sampleChunks = [
  { title: "2.5 Querying a Table", score: 0.975, snippet: "SELECT * FROM weather;\nSELECT city, temp_lo, temp_hi FROM weather;", source: "The SQL Language" },
  { title: "2.6 Joins Between Tables", score: 0.891, snippet: "SELECT * FROM weather JOIN cities ON weather.city = cities.name;", source: "The SQL Language" },
  { title: "7.2.1 Aggregate Functions", score: 0.764, snippet: "SELECT COUNT(*), AVG(temp_lo) FROM weather;", source: "Functions and Operators" },
]

export function RetrievalPanel({ chunks = sampleChunks, className, ...props }) {
  return (
    <div
      data-slot="retrieval-panel"
      className={cn("ml-11", className)}
      {...props}
    >
      <Accordion type="single" collapsible>
        <AccordionItem value="retrieval" className="border-0">
          <AccordionTrigger className="text-[11px] font-medium tracking-wide text-muted-foreground/50 uppercase hover:text-muted-foreground/80">
            Retrieval Inspector ({chunks.length} chunks)
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-2">
              {chunks.map((chunk, i) => (
                <div
                  key={i}
                  className="rounded-lg border border-border/50 bg-muted/20 px-3 py-2.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[13px] font-medium text-foreground/80">
                      {chunk.title}
                    </span>
                    <span
                      className={cn(
                        "text-[11px] font-mono",
                        chunk.score > 0.9
                          ? "text-green-600/70 dark:text-green-400/70"
                          : chunk.score > 0.8
                            ? "text-yellow-600/70 dark:text-yellow-400/70"
                            : "text-muted-foreground/50"
                      )}
                    >
                      {chunk.score.toFixed(3)}
                    </span>
                  </div>
                  <span className="text-[11px] text-muted-foreground/50">
                    {chunk.source}
                  </span>
                  <pre className="mt-1.5 overflow-x-auto rounded bg-black/5 p-2 text-[11px] leading-[1.4] text-muted-foreground/70 dark:bg-white/5">
                    {chunk.snippet}
                  </pre>
                </div>
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  )
}
