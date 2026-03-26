import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Card } from "../components/Card";
import { apiGet } from "../utils/api";

type VaultRead = { ok: boolean; path: string; content: string };

export function LogsPage() {
  const [rel, setRel] = useState<string>("execute_last_stderr.log");
  const q = useQuery({
    queryKey: ["vault", "read", rel],
    queryFn: () => apiGet<VaultRead>(`/api/vault/read?rel=${encodeURIComponent(rel)}`),
    refetchInterval: 2000
  });

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
      <Card title="Logs" subtitle="Quick access to last run logs" className="lg:col-span-2">
        <div className="space-y-2">
          {[
            "execute_last_stdout.log",
            "execute_last_stderr.log",
            "ideation_last.json",
            "execute_last_request.json"
          ].map((name) => (
            <button
              key={name}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-left text-sm hover:bg-white/10"
              onClick={() => setRel(name)}
            >
              {name}
            </button>
          ))}
        </div>
      </Card>

      <Card title="Preview" subtitle={rel} className="lg:col-span-3">
        {q.isLoading ? (
          <div className="text-sm text-slate-300">Loading...</div>
        ) : q.isError ? (
          <div className="text-sm text-red-300">{String(q.error)}</div>
        ) : (
          <pre className="max-h-[70vh] overflow-auto rounded-xl border border-white/10 bg-black/30 p-4 text-xs text-slate-100">
            {q.data?.content}
          </pre>
        )}
      </Card>
    </div>
  );
}

