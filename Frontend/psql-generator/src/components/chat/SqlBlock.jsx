import { cn } from "@/lib/utils"

export function SqlBlock({ sql, className, ...props }) {
  return (
    <div
      data-slot="sql-block"
      className={cn(
        "relative my-4 overflow-hidden rounded-lg bg-[#1d1d1f] dark:bg-[#0a0a0a]",
        className
      )}
      {...props}
    >
      <div className="flex items-center justify-between border-b border-white/5 px-4 py-2">
        <span className="text-[11px] font-medium tracking-wide text-white/40 uppercase">SQL</span>
        <button
          onClick={() => navigator.clipboard.writeText(sql)}
          className="text-[11px] font-medium tracking-wide text-white/40 transition-colors hover:text-white/70 uppercase"
        >
          Copy
        </button>
      </div>
      <div className="overflow-x-auto p-4">
        <pre className="text-[13px] leading-[1.6] text-[#e3e3e3] font-['SF_Mono','Cascadia_Code','Fira_Code',monospace]">
          <code>{sql}</code>
        </pre>
      </div>
    </div>
  )
}
