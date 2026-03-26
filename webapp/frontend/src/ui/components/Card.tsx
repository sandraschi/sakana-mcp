import { ReactNode } from "react";
import { cn } from "../utils/cn";

export function Card({
  title,
  subtitle,
  children,
  right,
  className
}: {
  title: string;
  subtitle?: string;
  right?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl shadow-[0_10px_45px_rgba(0,0,0,0.25)]",
        className
      )}
    >
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold tracking-wide">{title}</div>
          {subtitle ? <div className="text-xs text-slate-300">{subtitle}</div> : null}
        </div>
        {right ? <div>{right}</div> : null}
      </div>
      {children}
    </div>
  );
}

