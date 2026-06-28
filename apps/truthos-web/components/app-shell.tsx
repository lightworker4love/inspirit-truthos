"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { History, Home, Map, MessageCircle } from "lucide-react";

import { checkHealth, type HealthStatus } from "@/lib/api";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "首頁", icon: Home },
  { href: "/chat", label: "對話", icon: MessageCircle },
  { href: "/soul-map", label: "靈魂藍圖", icon: Map },
  { href: "/history", label: "記錄", icon: History },
];

function TruthLogo() {
  return (
    <div className="flex items-center gap-3">
      <svg
        aria-hidden="true"
        className="size-9 text-primary"
        fill="none"
        viewBox="0 0 40 40"
      >
        <path
          d="M20 4c6.4 5.2 10.6 10.6 10.6 16.1C30.6 26 26 31 20 36 14 31 9.4 26 9.4 20.1 9.4 14.6 13.6 9.2 20 4Z"
          stroke="currentColor"
          strokeLinejoin="round"
          strokeWidth="1.8"
        />
        <path
          d="M14.5 20h11M20 13.5v13"
          stroke="currentColor"
          strokeLinecap="round"
          strokeWidth="1.8"
        />
      </svg>
      <div>
        <p className="font-serif text-xl leading-none">TruthOS</p>
        <p className="text-xs text-muted-foreground">Life Blueprint</p>
      </div>
    </div>
  );
}

function HealthIndicator() {
  const [status, setStatus] = useState<HealthStatus | "checking">("checking");

  useEffect(() => {
    let mounted = true;

    async function refresh() {
      try {
        const result = await checkHealth();
        if (mounted) {
          setStatus(result.status);
        }
      } catch {
        if (mounted) {
          setStatus("offline");
        }
      }
    }

    refresh();
    const timer = window.setInterval(refresh, 60_000);
    return () => {
      mounted = false;
      window.clearInterval(timer);
    };
  }, []);

  const label = {
    checking: "正在確認服務",
    healthy: "服務正常",
    warming: "服務喚醒中...",
    partial: "後端部分降級",
    offline: "服務暫時離線",
  }[status];

  return (
    <div className="flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-2 text-sm text-muted-foreground">
      <span
        className={cn(
          "size-2 rounded-full",
          status === "checking" && "bg-muted-foreground",
          status === "healthy" && "bg-emerald-500",
          status === "warming" && "bg-sky-500",
          status === "partial" && "bg-amber-500",
          status === "offline" && "bg-red-500",
        )}
      />
      {label}
    </div>
  );
}

function DevModeBanner() {
  if (process.env.NODE_ENV !== "development") {
    return null;
  }

  return (
    <div className="border-b border-amber-700/30 bg-amber-950 px-4 py-2 text-center text-sm text-amber-100">
      Dev mode: connected to Railway production backend
    </div>
  );
}

function Navigation({ mobile = false }: { mobile?: boolean }) {
  const pathname = usePathname();

  return (
    <nav
      className={cn(
        mobile
          ? "grid grid-cols-4 gap-1"
          : "mt-10 flex flex-col gap-2",
      )}
    >
      {navItems.map((item) => {
        const Icon = item.icon;
        const active =
          item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

        return (
          <Link
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-3 text-sm transition-colors",
              active
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
              mobile && "flex-col gap-1 px-2 py-2 text-xs",
            )}
            href={item.href}
            key={item.href}
          >
            <Icon aria-hidden="true" className="size-4" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <DevModeBanner />
      <div className="flex min-h-screen">
        <aside className="hidden w-72 shrink-0 border-r border-border bg-surface/70 px-5 py-6 lg:block">
          <TruthLogo />
          <Navigation />
        </aside>

        <div className="flex min-h-screen flex-1 flex-col">
          <header className="sticky top-0 z-20 flex items-center justify-between border-b border-border bg-background/90 px-4 py-4 backdrop-blur md:px-8">
            <div className="lg:hidden">
              <TruthLogo />
            </div>
            <div className="hidden lg:block">
              <p className="text-sm text-muted-foreground">
                一個安靜、安全、可慢慢看見自己的空間
              </p>
            </div>
            <HealthIndicator />
          </header>

          <main className="flex-1 pb-24 lg:pb-0">{children}</main>

          <footer className="fixed inset-x-0 bottom-0 z-30 border-t border-border bg-surface/95 px-2 py-2 backdrop-blur lg:hidden">
            <Navigation mobile />
          </footer>
        </div>
      </div>
    </div>
  );
}
