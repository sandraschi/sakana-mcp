import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Card } from "../components/Card";
import { apiPost } from "../utils/api";

type ExecuteResponse = {
  ok: boolean;
  return_code: number;
  runtime_config: string;
  stdout_log: string;
  stderr_log: string;
};

export function ExecutePage() {
  const [ideasFile, setIdeasFile] = useState<string>("");
  const [ideaIdx, setIdeaIdx] = useState<number>(0);
  const [numWorkers, setNumWorkers] = useState<number>(3);
  const [maxDebugDepth, setMaxDebugDepth] = useState<number>(3);

  const exec = useMutation({
    mutationFn: () =>
      apiPost<ExecuteResponse>("/api/execute", {
        ideas_file: ideasFile || null,
        idea_idx: ideaIdx,
        num_workers: numWorkers,
        max_debug_depth: maxDebugDepth
      })
  });

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
      <Card
        title="Execute"
        subtitle="Docker sandbox run (GPU-enabled executor)"
        className="lg:col-span-2"
        right={
          <button
            className="rounded-xl border border-emerald-400/30 bg-emerald-400/10 px-3 py-2 text-xs text-emerald-200 hover:bg-emerald-400/15"
            onClick={() => exec.mutate()}
            disabled={exec.isPending}
          >
            {exec.isPending ? "Running..." : "research_execute"}
          </button>
        }
      >
        <div className="space-y-3">
          <label className="space-y-1">
            <div className="text-xs text-slate-300">ideas_file (optional)</div>
            <input
              className="w-full rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none ring-emerald-400/20 focus:ring-2"
              value={ideasFile}
              onChange={(e) => setIdeasFile(e.target.value)}
              placeholder="Leave empty to use research_vault default"
            />
          </label>

          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <label className="space-y-1">
              <div className="text-xs text-slate-300">idea_idx</div>
              <input
                type="number"
                className="w-full rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none ring-emerald-400/20 focus:ring-2"
                value={ideaIdx}
                onChange={(e) => setIdeaIdx(Number(e.target.value))}
                min={0}
              />
            </label>
            <label className="space-y-1">
              <div className="text-xs text-slate-300">num_workers</div>
              <input
                type="number"
                className="w-full rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none ring-emerald-400/20 focus:ring-2"
                value={numWorkers}
                onChange={(e) => setNumWorkers(Number(e.target.value))}
                min={1}
                max={16}
              />
            </label>
            <label className="space-y-1">
              <div className="text-xs text-slate-300">max_debug_depth</div>
              <input
                type="number"
                className="w-full rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none ring-emerald-400/20 focus:ring-2"
                value={maxDebugDepth}
                onChange={(e) => setMaxDebugDepth(Number(e.target.value))}
                min={0}
                max={10}
              />
            </label>
          </div>

          <div className="rounded-xl border border-white/10 bg-white/5 p-3 text-xs text-slate-300">
            This triggers Docker Compose `scientist-executor`. Ensure Docker is running and NVIDIA
            container runtime is configured.
          </div>

          {exec.isError ? (
            <div className="rounded-xl border border-red-400/20 bg-red-500/10 p-3 text-sm text-red-200">
              {String(exec.error)}
            </div>
          ) : null}
        </div>
      </Card>

      <Card title="Result" subtitle="Runtime config + logs" className="lg:col-span-3">
        {!exec.data ? (
          <div className="text-sm text-slate-300">Run execute to generate logs and config.</div>
        ) : (
          <div className="space-y-3 text-sm">
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              <div className="rounded-xl border border-white/10 bg-white/5 p-3">
                <div className="text-xs text-slate-300">ok</div>
                <div className="font-semibold">{String(exec.data.ok)}</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-3">
                <div className="text-xs text-slate-300">return_code</div>
                <div className="font-semibold">{exec.data.return_code}</div>
              </div>
            </div>

            <div className="rounded-xl border border-white/10 bg-white/5 p-3">
              <div className="text-xs text-slate-300">runtime_config</div>
              <div className="break-all text-slate-100">{exec.data.runtime_config}</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-3">
              <div className="text-xs text-slate-300">stdout_log</div>
              <div className="break-all text-slate-100">{exec.data.stdout_log}</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-3">
              <div className="text-xs text-slate-300">stderr_log</div>
              <div className="break-all text-slate-100">{exec.data.stderr_log}</div>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

