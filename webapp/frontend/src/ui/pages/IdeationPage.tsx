import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Card } from "../components/Card";
import { apiPost } from "../utils/api";

type IdeateResponse = {
  ok: boolean;
  mode: string;
  ideation_error: string | null;
  hypotheses: Array<{ id: string; title: string; hypothesis: string }>;
  research_vault: string;
};

export function IdeationPage() {
  const [codebaseHint, setCodebaseHint] = useState<string>("");
  const [model, setModel] = useState<string>("gemini-2.5-flash");
  const [maxNum, setMaxNum] = useState<number>(5);
  const [reflections, setReflections] = useState<number>(3);

  const ideate = useMutation({
    mutationFn: () =>
      apiPost<IdeateResponse>("/api/ideate", {
        codebase_hint: codebaseHint || null,
        model,
        max_num_generations: maxNum,
        num_reflections: reflections
      })
  });

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
      <Card
        title="Ideation"
        subtitle="Generate 5 hypotheses (AI-Scientist v2 if available)"
        className="lg:col-span-2"
        right={
          <button
            className="rounded-xl border border-amber-400/30 bg-amber-400/10 px-3 py-2 text-xs text-amber-200 hover:bg-amber-400/15"
            onClick={() => ideate.mutate()}
            disabled={ideate.isPending}
          >
            {ideate.isPending ? "Running..." : "research_ideate"}
          </button>
        }
      >
        <div className="space-y-3">
          <div>
            <div className="mb-1 text-xs text-slate-300">codebase_hint</div>
            <textarea
              className="h-28 w-full resize-none rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-slate-100 outline-none ring-amber-400/20 focus:ring-2"
              value={codebaseHint}
              onChange={(e) => setCodebaseHint(e.target.value)}
              placeholder="What should the Scientist focus on? (datasets, task, repo constraints, novelty target)"
            />
          </div>

          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <label className="space-y-1">
              <div className="text-xs text-slate-300">model</div>
              <input
                className="w-full rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none ring-amber-400/20 focus:ring-2"
                value={model}
                onChange={(e) => setModel(e.target.value)}
              />
            </label>
            <label className="space-y-1">
              <div className="text-xs text-slate-300">max_num_generations</div>
              <input
                type="number"
                className="w-full rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none ring-amber-400/20 focus:ring-2"
                value={maxNum}
                onChange={(e) => setMaxNum(Number(e.target.value))}
                min={1}
                max={50}
              />
            </label>
            <label className="space-y-1">
              <div className="text-xs text-slate-300">num_reflections</div>
              <input
                type="number"
                className="w-full rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none ring-amber-400/20 focus:ring-2"
                value={reflections}
                onChange={(e) => setReflections(Number(e.target.value))}
                min={1}
                max={10}
              />
            </label>
          </div>

          {ideate.isError ? (
            <div className="rounded-xl border border-red-400/20 bg-red-500/10 p-3 text-sm text-red-200">
              {String(ideate.error)}
            </div>
          ) : null}
          {ideate.data?.ideation_error ? (
            <div className="rounded-xl border border-amber-400/20 bg-amber-500/10 p-3 text-xs text-amber-200">
              ideation_error: {ideate.data.ideation_error}
            </div>
          ) : null}
        </div>
      </Card>

      <Card title="Hypotheses" subtitle="Top 5" className="lg:col-span-3">
        {!ideate.data ? (
          <div className="text-sm text-slate-300">Run ideation to populate hypotheses.</div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-300">
              <div>mode: {ideate.data.mode}</div>
              <div>vault: {ideate.data.research_vault}</div>
            </div>
            <div className="grid grid-cols-1 gap-3">
              {ideate.data.hypotheses.map((h) => (
                <div
                  key={h.id}
                  className="rounded-2xl border border-white/10 bg-white/5 p-4"
                >
                  <div className="mb-1 flex items-center justify-between gap-2">
                    <div className="text-xs text-slate-300">{h.id}</div>
                    <div className="text-sm font-semibold">{h.title}</div>
                  </div>
                  <div className="text-sm text-slate-200">{h.hypothesis}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

