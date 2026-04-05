import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Card } from "../components/Card";
import { apiGet } from "../utils/api";

type Task = {
  task_id: string;
  title: string;
  domain: string;
  difficulty: string;
  summary: string;
  success_criteria: string[];
  starter_prompt: string;
};

type TaskResponse = {
  ok: boolean;
  count: number;
  domains: string[];
  tasks: Task[];
};

type PlanResponse = {
  ok: boolean;
  task: Task;
  plan: Array<{ step: number; tool: string; args: Record<string, unknown>; goal: string }>;
};

export function LibraryPage() {
  const [domain, setDomain] = useState<string>("");
  const [taskId, setTaskId] = useState<string>("");

  const tasks = useQuery({
    queryKey: ["library", domain],
    queryFn: () =>
      apiGet<TaskResponse>(
        `/api/library/tasks${domain ? `?domain=${encodeURIComponent(domain)}` : ""}`
      ),
  });

  const plan = useQuery({
    queryKey: ["workflow-plan", taskId],
    queryFn: () => apiGet<PlanResponse>(`/api/workflow/plan?task_id=${encodeURIComponent(taskId)}`),
    enabled: Boolean(taskId),
  });

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
      <Card title="Task Library" subtitle="Sample and custom research missions" className="lg:col-span-3">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <button
            className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs hover:bg-white/10"
            onClick={() => setDomain("")}
          >
            all
          </button>
          {(tasks.data?.domains ?? []).map((d) => (
            <button
              key={d}
              className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs hover:bg-white/10"
              onClick={() => setDomain(d)}
            >
              {d}
            </button>
          ))}
        </div>

        {tasks.isLoading ? (
          <div className="text-sm text-slate-300">Loading tasks...</div>
        ) : tasks.isError ? (
          <div className="text-sm text-red-300">{String(tasks.error)}</div>
        ) : (
          <div className="space-y-3">
            {(tasks.data?.tasks ?? []).map((t) => (
              <button
                key={t.task_id}
                className="w-full rounded-2xl border border-white/10 bg-white/5 p-4 text-left hover:bg-white/10"
                onClick={() => setTaskId(t.task_id)}
              >
                <div className="mb-1 flex items-center justify-between gap-2">
                  <div className="text-sm font-semibold">{t.title}</div>
                  <div className="text-xs text-slate-300">
                    {t.domain} · {t.difficulty}
                  </div>
                </div>
                <div className="text-sm text-slate-200">{t.summary}</div>
                <div className="mt-2 text-xs text-slate-300">task_id: {t.task_id}</div>
              </button>
            ))}
          </div>
        )}
      </Card>

      <Card title="Agentic Workflow" subtitle={taskId || "Pick a task to generate plan"} className="lg:col-span-2">
        {!taskId ? (
          <div className="text-sm text-slate-300">Select a task to generate a guided workflow.</div>
        ) : plan.isLoading ? (
          <div className="text-sm text-slate-300">Generating workflow...</div>
        ) : plan.isError ? (
          <div className="text-sm text-red-300">{String(plan.error)}</div>
        ) : (
          <div className="space-y-3">
            {(plan.data?.plan ?? []).map((p) => (
              <div key={p.step} className="rounded-xl border border-white/10 bg-white/5 p-3">
                <div className="flex items-center justify-between text-xs text-slate-300">
                  <span>step {p.step}</span>
                  <span>{p.tool}</span>
                </div>
                <div className="mt-1 text-sm text-slate-100">{p.goal}</div>
                <pre className="mt-2 overflow-auto rounded-lg bg-black/30 p-2 text-[11px] text-slate-200">
                  {JSON.stringify(p.args, null, 2)}
                </pre>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

