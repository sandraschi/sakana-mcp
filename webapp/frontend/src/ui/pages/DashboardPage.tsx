import { useQuery } from "@tanstack/react-query";
import { Card } from "../components/Card";
import { apiGet } from "../utils/api";

type Health = {
  ok: boolean;
  repo_root: string;
  research_vault: string;
  ai_scientist_v2: string;
};

type Status = {
  ok: boolean;
  status: string;
  tree_health: {
    good_nodes: number;
    buggy_nodes: number;
    ratio_good_to_buggy: number | null;
  };
};

export function DashboardPage() {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: () => apiGet<Health>("/api/health")
  });
  const status = useQuery({
    queryKey: ["status"],
    queryFn: () => apiGet<Status>("/api/status"),
    refetchInterval: 3000
  });

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <Card title="System" subtitle="Connectivity + paths">
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

      <Card title="Tree Health" subtitle="Buggy vs non-buggy nodes">
        {status.isLoading ? (
          <div className="text-sm text-slate-300">Loading...</div>
        ) : status.isError ? (
          <div className="text-sm text-red-300">{String(status.error)}</div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-baseline justify-between">
              <div className="text-2xl font-semibold">{status.data?.status}</div>
              <div className="text-xs text-slate-300">auto-refresh 3s</div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="rounded-xl border border-white/10 bg-white/5 p-3">
                <div className="text-slate-300">good</div>
                <div className="text-lg font-semibold">{status.data?.tree_health.good_nodes}</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-3">
                <div className="text-slate-300">buggy</div>
                <div className="text-lg font-semibold">{status.data?.tree_health.buggy_nodes}</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-3">
                <div className="text-slate-300">ratio</div>
                <div className="text-lg font-semibold">
                  {status.data?.tree_health.ratio_good_to_buggy === null ||
                  status.data?.tree_health.ratio_good_to_buggy === undefined
                    ? "—"
                    : status.data.tree_health.ratio_good_to_buggy.toFixed(2)}
                </div>
              </div>
            </div>
          </div>
        )}
      </Card>

      <Card title="Next Actions" subtitle="Typical loop">
        <ol className="space-y-2 text-sm text-slate-200">
          <li className="rounded-xl border border-white/10 bg-white/5 p-3">
            Ideation: generate hypotheses
          </li>
          <li className="rounded-xl border border-white/10 bg-white/5 p-3">
            Execute: run Docker sandbox experiment
          </li>
          <li className="rounded-xl border border-white/10 bg-white/5 p-3">
            Status: monitor stage progress
          </li>
          <li className="rounded-xl border border-white/10 bg-white/5 p-3">
            Review: VLM critique of figures/captions
          </li>
        </ol>
      </Card>
    </div>
  );
}

