import { useQuery } from "@tanstack/react-query";
import { Card } from "../components/Card";
import { apiGet } from "../utils/api";

type Status = {
  ok: boolean;
  status: string;
  runtime: { mode: "live" | "fallback"; mock: boolean; reason: string };
  docker: {
    docker_cli_available: boolean;
    docker_daemon_reachable: boolean;
    compose_file_exists: boolean;
    required_services: string[];
    service_status: Record<string, { present: boolean; running: boolean; state: string }>;
  };
  tree_health: { good_nodes: number; buggy_nodes: number; ratio_good_to_buggy: number | null };
  stages: Array<{
    stage: string;
    total_nodes: number;
    good_nodes: number;
    buggy_nodes: number;
    best_metric: string | null;
    path: string;
  }>;
  research_vault: string;
};

export function StatusPage() {
  const q = useQuery({
    queryKey: ["status"],
    queryFn: () => apiGet<Status>("/api/status"),
    refetchInterval: 2000
  });

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
      <Card title="Status" subtitle="Tree health + stages" className="lg:col-span-2">
        {q.isLoading ? (
          <div className="text-sm text-slate-300">Loading...</div>
        ) : q.isError ? (
          <div className="text-sm text-red-300">{String(q.error)}</div>
        ) : (
          <div className="space-y-3">
            <div className="text-xs text-slate-300">vault: {q.data?.research_vault}</div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-2 text-xs text-slate-300">
              mode: {q.data?.runtime.mode === "live" ? "LIVE" : "FALLBACK [MOCK]"} -{" "}
              {q.data?.runtime.reason}
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="rounded-xl border border-white/10 bg-white/5 p-3">
                <div className="text-slate-300">good</div>
                <div className="text-lg font-semibold">{q.data?.tree_health.good_nodes}</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-3">
                <div className="text-slate-300">buggy</div>
                <div className="text-lg font-semibold">{q.data?.tree_health.buggy_nodes}</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-3">
                <div className="text-slate-300">ratio</div>
                <div className="text-lg font-semibold">
                  {q.data?.tree_health.ratio_good_to_buggy === null ||
                  q.data?.tree_health.ratio_good_to_buggy === undefined
                    ? "—"
                    : q.data.tree_health.ratio_good_to_buggy.toFixed(2)}
                </div>
              </div>
            </div>
          </div>
        )}
      </Card>

      <Card title="Stages + Docker" subtitle="Tree and container readiness" className="lg:col-span-3">
        <div className="mb-3 grid grid-cols-1 gap-2 md:grid-cols-2">
          <div className="rounded-xl border border-white/10 bg-white/5 p-3 text-xs">
            docker cli: {q.data?.docker.docker_cli_available ? "installed" : "missing"}
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-3 text-xs">
            daemon: {q.data?.docker.docker_daemon_reachable ? "reachable" : "unreachable"}
          </div>
        </div>
        <div className="mb-3 space-y-2">
          {(q.data?.docker.required_services ?? []).map((name) => {
            const info = q.data?.docker.service_status?.[name];
            return (
              <div key={name} className="rounded-xl border border-white/10 bg-white/5 p-3 text-xs">
                <span className="font-semibold">{name}</span>:{" "}
                {info?.present ? (info.running ? "running" : `not running (${info.state})`) : "not created"}
              </div>
            );
          })}
        </div>
        {!q.data?.stages?.length ? (
          <div className="text-sm text-slate-300">
            No stage progress found yet. Run Execute first.
          </div>
        ) : (
          <div className="space-y-2">
            {q.data.stages.map((s, idx) => (
              <div
                key={`${s.stage}-${idx}`}
                className="rounded-2xl border border-white/10 bg-white/5 p-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="text-sm font-semibold">{s.stage}</div>
                  <div className="text-xs text-slate-300">best_metric: {s.best_metric ?? "—"}</div>
                </div>
                <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
                  <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                    <div className="text-slate-300">total</div>
                    <div className="text-base font-semibold">{s.total_nodes}</div>
                  </div>
                  <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                    <div className="text-slate-300">good</div>
                    <div className="text-base font-semibold">{s.good_nodes}</div>
                  </div>
                  <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                    <div className="text-slate-300">buggy</div>
                    <div className="text-base font-semibold">{s.buggy_nodes}</div>
                  </div>
                </div>
                <div className="mt-2 break-all text-xs text-slate-400">{s.path}</div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

