import { useQuery } from "@tanstack/react-query";
import { Card } from "../components/Card";
import { apiGet } from "../utils/api";

type Health = {
  ok: boolean;
  repo_root: string;
  research_vault: string;
  ai_scientist_v2: string;
  runtime: { mode: "live" | "fallback"; mock: boolean; reason: string };
  docker: {
    docker_cli_available: boolean;
    docker_daemon_reachable: boolean;
  };
};

type Status = {
  ok: boolean;
  status: string;
  runtime: { mode: "live" | "fallback"; mock: boolean; reason: string };
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
  const liveReady =
    health.data?.runtime.mode === "live" &&
    Boolean(health.data?.docker.docker_cli_available) &&
    Boolean(health.data?.docker.docker_daemon_reachable);

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl">
        <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
          <div className="text-lg font-semibold">What this can do</div>
          <div className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-xs text-slate-200">
            {status.data?.runtime.mode === "live" ? "LIVE MODE" : "FALLBACK [MOCK] MODE"}
          </div>
        </div>
        <div className="text-sm text-slate-200">
          Research v2 is an autonomous research control plane: it generates hypotheses, runs
          sandboxed experiments, monitors buggy vs non-buggy tree nodes, and reviews manuscript
          figures/captions for scientific quality.
        </div>
        <div
          className={
            liveReady
              ? "mt-3 rounded-xl border border-emerald-400/20 bg-emerald-500/10 p-3 text-sm text-emerald-200"
              : "mt-3 rounded-xl border border-amber-400/20 bg-amber-500/10 p-3 text-sm text-amber-200"
          }
        >
          {liveReady
            ? "Complete setup detected. Live mode active."
            : "Complete setup required. Currently mock only."}
        </div>
      </div>

      {!liveReady ? (
        <div className="rounded-2xl border border-amber-400/20 bg-amber-500/10 p-5">
          <div className="mb-2 text-sm font-semibold text-amber-200">Go Live Checklist</div>
          <ol className="space-y-2 text-sm text-amber-100">
            <li className="rounded-xl border border-amber-300/20 bg-black/20 p-3">
              {health.data?.docker.docker_cli_available ? "DONE" : "TODO"} - Install Docker CLI
            </li>
            <li className="rounded-xl border border-amber-300/20 bg-black/20 p-3">
              {health.data?.docker.docker_daemon_reachable ? "DONE" : "TODO"} - Start Docker daemon
            </li>
            <li className="rounded-xl border border-amber-300/20 bg-black/20 p-3">
              {health.data?.runtime.mode === "live" ? "DONE" : "TODO"} - Enable live ideation
              (set keys/vendor path so fallback is not used)
            </li>
            <li className="rounded-xl border border-amber-300/20 bg-black/20 p-3">
              TODO - Run one full loop: Ideation to Execute to Status to Review
            </li>
          </ol>
          <div className="mt-2 text-xs text-amber-200/90">
            This checklist auto-hides when setup is complete.
          </div>
        </div>
      ) : null}

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
            <div className="flex justify-between gap-3">
              <span className="text-slate-300">runtime_mode</span>
              <span className="text-right">
                {health.data?.runtime.mode === "live" ? "LIVE" : "FALLBACK [MOCK]"}
              </span>
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
              <div className="text-xs text-slate-300">
                {status.data?.runtime.mode === "live" ? "LIVE" : "FALLBACK [MOCK]"}
              </div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-2 text-xs text-slate-300">
              {status.data?.runtime.reason}
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

      <Card title="Docker Readiness" subtitle="Required for live execution">
        {health.isLoading ? (
          <div className="text-sm text-slate-300">Loading...</div>
        ) : (
          <div className="space-y-2 text-xs">
            <div className="rounded-xl border border-white/10 bg-white/5 p-3">
              docker cli: {health.data?.docker.docker_cli_available ? "installed" : "missing"}
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-3">
              daemon: {health.data?.docker.docker_daemon_reachable ? "reachable" : "unreachable"}
            </div>
          </div>
        )}
      </Card>
      </div>
    </div>
  );
}

