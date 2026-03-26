import { useQuery } from "@tanstack/react-query";
import { Card } from "../components/Card";
import { apiGet } from "../utils/api";

type Health = {
  ok: boolean;
  repo_root: string;
  research_vault: string;
  ai_scientist_v2: string;
};

export function SettingsPage() {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: () => apiGet<Health>("/api/health")
  });

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <Card title="Paths" subtitle="Backend resolved paths">
        {health.isLoading ? (
          <div className="text-sm text-slate-300">Loading...</div>
        ) : health.isError ? (
          <div className="text-sm text-red-300">{String(health.error)}</div>
        ) : (
          <div className="space-y-2 text-xs text-slate-200">
            <div className="flex justify-between gap-3">
              <span className="text-slate-300">repo_root</span>
              <span className="truncate text-right">{health.data?.repo_root}</span>
            </div>
            <div className="flex justify-between gap-3">
              <span className="text-slate-300">research_vault</span>
              <span className="truncate text-right">{health.data?.research_vault}</span>
            </div>
            <div className="flex justify-between gap-3">
              <span className="text-slate-300">ai_scientist_v2</span>
              <span className="truncate text-right">{health.data?.ai_scientist_v2}</span>
            </div>
          </div>
        )}
      </Card>

      <Card title="Environment" subtitle="Set via your shell/session">
        <div className="space-y-2 text-sm text-slate-200">
          <div className="rounded-xl border border-white/10 bg-white/5 p-3">
            <div className="text-xs text-slate-300">GEMINI_API_KEY</div>
            <div className="text-xs text-slate-400">required for Gemini-backed ideation/review</div>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-3">
            <div className="text-xs text-slate-300">S2_API_KEY</div>
            <div className="text-xs text-slate-400">Semantic Scholar throughput</div>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-3">
            <div className="text-xs text-slate-300">RESEARCH_VAULT_PATH</div>
            <div className="text-xs text-slate-400">defaults to repo research_vault</div>
          </div>
        </div>
      </Card>

      <Card title="Ports" subtitle="Fleet-compliant allocation">
        <div className="space-y-2 text-sm text-slate-200">
          <div className="rounded-xl border border-white/10 bg-white/5 p-3">
            Frontend: <span className="font-semibold">10720</span>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-3">
            Backend: <span className="font-semibold">10721</span>
          </div>
        </div>
      </Card>
    </div>
  );
}

