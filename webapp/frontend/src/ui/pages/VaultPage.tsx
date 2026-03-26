import { useMutation, useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Card } from "../components/Card";
import { apiGet } from "../utils/api";

type VaultList = {
  ok: boolean;
  type: "dir" | "file";
  rel?: string;
  entries?: Array<{ name: string; type: "file" | "dir"; size: number | null }>;
};

type VaultRead = { ok: boolean; path: string; content: string };

export function VaultPage() {
  const [rel, setRel] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<string>("");

  const list = useQuery({
    queryKey: ["vault", "list", rel],
    queryFn: () => apiGet<VaultList>(`/api/vault/list?rel=${encodeURIComponent(rel)}`)
  });

  const reader = useMutation({
    mutationFn: (fileRel: string) =>
      apiGet<VaultRead>(`/api/vault/read?rel=${encodeURIComponent(fileRel)}`)
  });

  const breadcrumbs = useMemo(() => {
    const parts = rel.split(/[\\/]/).filter(Boolean);
    const acc: Array<{ label: string; rel: string }> = [{ label: "vault", rel: "" }];
    let cur = "";
    for (const p of parts) {
      cur = cur ? `${cur}/${p}` : p;
      acc.push({ label: p, rel: cur });
    }
    return acc;
  }, [rel]);

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
      <Card title="Vault" subtitle="Browse research_vault artifacts" className="lg:col-span-2">
        <div className="mb-3 flex flex-wrap items-center gap-2 text-xs text-slate-300">
          {breadcrumbs.map((b, idx) => (
            <button
              key={`${b.rel}-${idx}`}
              className="rounded-full border border-white/10 bg-white/5 px-3 py-1 hover:bg-white/10"
              onClick={() => {
                setRel(b.rel);
                setSelectedFile("");
              }}
            >
              {b.label}
            </button>
          ))}
        </div>

        {list.isLoading ? (
          <div className="text-sm text-slate-300">Loading...</div>
        ) : list.isError ? (
          <div className="text-sm text-red-300">{String(list.error)}</div>
        ) : (
          <div className="space-y-2">
            {(list.data?.entries ?? []).map((e) => (
              <button
                key={e.name}
                className="flex w-full items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-left text-sm hover:bg-white/10"
                onClick={() => {
                  if (e.type === "dir") {
                    const next = rel ? `${rel}/${e.name}` : e.name;
                    setRel(next);
                    setSelectedFile("");
                  } else {
                    const next = rel ? `${rel}/${e.name}` : e.name;
                    setSelectedFile(next);
                    reader.mutate(next);
                  }
                }}
              >
                <div className="truncate">
                  <span className="text-slate-300">{e.type === "dir" ? "DIR" : "FILE"}</span>{" "}
                  <span className="text-slate-100">{e.name}</span>
                </div>
                <div className="text-xs text-slate-400">
                  {e.type === "file" ? (e.size ?? 0).toLocaleString() : ""}
                </div>
              </button>
            ))}
          </div>
        )}
      </Card>

      <Card title="Preview" subtitle={selectedFile || "Select a file"} className="lg:col-span-3">
        {reader.isPending ? (
          <div className="text-sm text-slate-300">Loading file...</div>
        ) : reader.isError ? (
          <div className="text-sm text-red-300">{String(reader.error)}</div>
        ) : reader.data ? (
          <pre className="max-h-[70vh] overflow-auto rounded-xl border border-white/10 bg-black/30 p-4 text-xs text-slate-100">
            {reader.data.content}
          </pre>
        ) : (
          <div className="text-sm text-slate-300">Pick an artifact to preview it.</div>
        )}
      </Card>
    </div>
  );
}

