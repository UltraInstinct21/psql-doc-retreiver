import { useState, useCallback } from "react"
import { cn } from "@/lib/utils"
import { Check, Copy } from "lucide-react"

export function SqlBlock({ sql, className, ...props }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(sql).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    })
  }, [sql])

  return (
    <div
      data-slot="sql-block"
      className={cn(
        "relative overflow-hidden rounded-[8px] bg-cocoa-black ring-1 ring-warm-sand/10",
        className
      )}
      {...props}
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-warm-sand/8 px-4 py-2">
        <div className="flex items-center gap-2">
          <span className="size-2 rounded-full bg-mint-keyhole/40" />
          <span className="text-[11px] font-medium tracking-[0.06em] uppercase text-stone/60">SQL</span>
        </div>
        <button
          onClick={handleCopy}
          className="inline-flex items-center gap-1 rounded-pill px-2.5 py-1 text-[11px] font-medium text-stone/60 transition-colors hover:text-cream-mist hover:bg-deep-plum"
        >
          {copied ? (
            <><Check className="size-3 text-mint-keyhole" /> Copied</>
          ) : (
            <><Copy className="size-3" /> Copy</>
          )}
        </button>
      </div>

      {/* Code */}
      <div className="overflow-x-auto p-4">
        <pre className="text-[13px] leading-[1.6] text-cream-mist/90 font-mono">
          <code>{sql}</code>
        </pre>
      </div>
    </div>
  )
}
