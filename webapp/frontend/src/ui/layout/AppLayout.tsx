import { ReactNode, useMemo, useState } from "react";
import { NavLink } from "react-router-dom";
import { cn } from "../utils/cn";

const NAV = [
  { to: "/", label: "Dashboard" },
  { to: "/ideation", label: "Ideation" },
  { to: "/execute", label: "Execute" },
  { to: "/status", label: "Status" },
  { to: "/review", label: "Review" },
  { to: "/library", label: "Library" },
  { to: "/vault", label: "Vault" },
  { to: "/logs", label: "Logs" },
  { to: "/settings", label: "Settings" }
] as const;

export function AppLayout({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState<boolean>(() => {
    const raw = localStorage.getItem("sakana.sidebar.collapsed");
    return raw === "1";
  });

  const shell = useMemo(
    () => ({
      sidebarWidth: collapsed ? "w-[72px]" : "w-[260px]"
    }),
    [collapsed]
  );

  return (
    <div className="h-full w-full">
      <div className="mx-auto flex h-full max-w-[1600px] gap-4 p-4">
        <aside
          className={cn(
            "rounded-2xl border border-white/10 bg-slateGlass backdrop-blur-xl shadow-[0_12px_50px_rgba(0,0,0,0.35)]",
            shell.sidebarWidth
          )}
        >
          <div className="flex items-center justify-between px-4 py-4">
            <div className={cn("font-semibold tracking-wide", collapsed && "hidden")}>
              sakana-mcp
            </div>
            <button
              className="rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-xs text-slate-200 hover:bg-white/10"
              onClick={() => {
                const next = !collapsed;
                setCollapsed(next);
                localStorage.setItem("sakana.sidebar.collapsed", next ? "1" : "0");
              }}
            >
              {collapsed ? ">" : "<"}
            </button>
          </div>

          <nav className="px-2 pb-3">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    "my-1 flex items-center gap-3 rounded-xl px-3 py-2 text-sm text-slate-200 hover:bg-white/10",
                    isActive && "bg-white/10 ring-1 ring-amber-400/30",
                    collapsed && "justify-center"
                  )
                }
              >
                <span className="h-2 w-2 rounded-full bg-amber-400/80" />
                <span className={cn(collapsed && "hidden")}>{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="flex min-w-0 flex-1 flex-col gap-4">
          <header className="rounded-2xl border border-white/10 bg-slateGlass px-5 py-4 backdrop-blur-xl">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-sm text-slate-300">
                  Research v2: plan ideas, run experiments, review papers
                </div>
                <div className="text-lg font-semibold tracking-wide">Sakana AI Scientist v2</div>
                <div className="text-xs text-slate-400">
                  For first-time users: this app guides full research loops from hypothesis to review.
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-300">
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
                  Frontend: 10862
                </span>
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
                  Backend: 10863
                </span>
              </div>
            </div>
          </header>

          <section className="min-h-0 flex-1">{children}</section>
        </main>
      </div>
    </div>
  );
}

