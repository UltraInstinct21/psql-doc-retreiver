import { Apple } from "lucide-react"
import { cn } from "@/lib/utils"

const navLinks = [
  { label: "Store", href: "#" },
  { label: "Mac", href: "#" },
  { label: "iPad", href: "#" },
  { label: "iPhone", href: "#" },
  { label: "Watch", href: "#" },
  { label: "Vision", href: "#" },
  { label: "AirPods", href: "#" },
  { label: "TV & Home", href: "#" },
  { label: "Entertainment", href: "#" },
  { label: "Accessories", href: "#" },
  { label: "Support", href: "#" },
]

export function GlobalNav({ className, ...props }) {
  return (
    <nav
      data-slot="global-nav"
      className={cn(
        "fixed top-0 right-0 left-0 z-50 flex h-11 items-center justify-center bg-black px-4",
        className
      )}
      {...props}
    >
      <div className="flex w-full max-w-[1440px] items-center justify-between">
        <div className="flex items-center gap-5 max-lg:hidden">
          {navLinks.slice(0, 5).map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-[12px] font-normal tracking-[-0.12px] text-white/80 transition-colors hover:text-white"
            >
              {link.label}
            </a>
          ))}
        </div>
        <div className="flex items-center gap-5 lg:hidden">
          <button className="text-white/80 hover:text-white" aria-label="Menu">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <rect x="2" y="4" width="14" height="1.5" rx="0.75" fill="currentColor" />
              <rect x="2" y="8.5" width="14" height="1.5" rx="0.75" fill="currentColor" />
              <rect x="2" y="13" width="14" height="1.5" rx="0.75" fill="currentColor" />
            </svg>
          </button>
        </div>
        <div className="flex items-center gap-5">
          <a href="#" className="text-white/80 transition-colors hover:text-white" aria-label="Apple">
            <Apple className="size-4" fill="currentColor" />
          </a>
        </div>
        <div className="flex items-center gap-5 max-lg:hidden">
          {navLinks.slice(5).map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-[12px] font-normal tracking-[-0.12px] text-white/80 transition-colors hover:text-white"
            >
              {link.label}
            </a>
          ))}
        </div>
        <div className="flex items-center gap-4">
          <button className="text-white/80 hover:text-white" aria-label="Search">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <circle cx="8" cy="8" r="5.5" stroke="currentColor" strokeWidth="1.5" />
              <path d="M12 12L16 16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
          <button className="text-white/80 hover:text-white" aria-label="Bag">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M4 6H14L13 14H5L4 6Z" stroke="currentColor" strokeWidth="1.2" />
              <path d="M6.5 6V4.5C6.5 3.12 7.62 2 9 2C10.38 2 11.5 3.12 11.5 4.5V6" stroke="currentColor" strokeWidth="1.2" />
            </svg>
          </button>
        </div>
      </div>
    </nav>
  )
}
