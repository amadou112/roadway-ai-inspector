"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { useAuth } from "@/lib/auth-context";
import { visibleNavItems } from "./nav-config";

export function Sidebar() {
  const { user } = useAuth();
  const pathname = usePathname();
  const items = visibleNavItems(user?.role);

  return (
    <aside className="hidden w-64 shrink-0 flex-col bg-federal-950 text-white md:flex">
      <div className="flex items-center gap-2 border-b border-white/10 px-5 py-5">
        <span className="text-2xl">🛣️</span>
        <div className="leading-tight">
          <p className="text-sm font-bold">Roadway AI</p>
          <p className="text-[11px] text-federal-100/70">Inspector &amp; Design Assistant</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {items.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                active ? "bg-federal-700 text-white" : "text-federal-100/80 hover:bg-white/5 hover:text-white"
              )}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-white/10 px-5 py-4 text-[11px] text-federal-100/60">
        Delaware DOT Demo Environment
      </div>
    </aside>
  );
}
