import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

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
        "fixed top-0 right-0 left-0 z-40 flex h-13 items-center border-b border-border/40 bg-background/80 backdrop-blur-2xl px-6",
        className
      )}
      style={{ backdropFilter: "saturate(180%) blur(20px)" }}
      {...props}
    >
      <div className="mx-auto flex w-full max-w-[1440px] items-center justify-between">
        <span className="text-[21px] font-semibold tracking-[0.231px] text-ink">
          {title}
        </span>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            className="text-[13px] font-normal tracking-[-0.12px] text-muted-foreground"
            onClick={onHistoryClick}
          >
            History
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="text-[13px] font-normal tracking-[-0.12px] text-muted-foreground"
            onClick={onSettingsClick}
          >
            Settings
          </Button>
        </div>
      </div>
    </div>
  )
}
