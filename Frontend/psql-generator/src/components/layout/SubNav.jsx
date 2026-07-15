import { cn } from "@/lib/utils"
import { History, Settings } from "lucide-react"

export function SubNav({
  className,
  title = "AI PostgreSQL Query Assistant",
  onHistoryClick,
  onSettingsClick,
  ...props
}) {
  return (
    <div
      data-slot="sub-nav"
      className={cn(
        "fixed top-0 right-0 left-0 z-40 flex h-13 items-center border-b border-warm-sand/10 bg-cocoa-black/90 backdrop-blur-2xl px-4 sm:px-6",
        className
      )}
      {...props}
    >
      <div className="mx-auto flex w-full max-w-[1200px] items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-mint-keyhole/10">
            <span className="text-[13px] font-medium text-mint-keyhole">Pg</span>
          </div>
          <span className="truncate text-[15px] font-medium tracking-[0.02em] text-cream-mist">
            {title}
          </span>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={onHistoryClick}
            className="inline-flex items-center gap-1.5 rounded-pill px-3 py-1.5 text-[13px] font-medium text-stone transition-colors hover:text-cream-mist hover:bg-deep-plum/60 active:bg-deep-plum"
          >
            <History className="size-3.5" />
            <span className="hidden sm:inline">History</span>
          </button>
          <button
            onClick={onSettingsClick}
            className="inline-flex items-center gap-1.5 rounded-pill px-3 py-1.5 text-[13px] font-medium text-stone transition-colors hover:text-cream-mist hover:bg-deep-plum/60 active:bg-deep-plum"
          >
            <Settings className="size-3.5" />
            <span className="hidden sm:inline">Settings</span>
          </button>
        </div>
      </div>
    </div>
  )
}
