export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export const TOOLS = { jaeger: "http://localhost:16686", temporal: "http://localhost:8080", prometheus: "http://localhost:9090", docs: `${API}/docs` };

export type Scenario = { id: string; category: string; level: string; title: string; steps: string[] };
export type StepResult = { step: number; sql: string; command: string | null; rowcount: number; columns: string[]; rows: unknown[][]; ms: number };
export type RunResult = { scenario_id: string; status: "ok" | "failed"; duration_ms: number; steps: StepResult[]; error?: string | null };
export type RunResponse = { mode: string; workflow_id: string | null; summary: { total: number; ok: number; failed: number }; results: RunResult[] };
export type User = { id: number; email: string; full_name: string; role: string };

async function call<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const res = await fetch(`${API}/api/v1${path}`, {
    ...init,
    headers: { ...(init.headers ?? {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail ?? res.statusText);
    throw Object.assign(new Error(detail), { status: res.status });
  }
  return res.json();
}

const json = (body: unknown): RequestInit => ({ method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

export const auth = {
  register: (email: string, full_name: string, password: string) => call<User>("/auth/register", json({ email, full_name, password })),
  login: (email: string, password: string) =>
    call<{ access_token: string }>("/auth/login", { method: "POST", body: new URLSearchParams({ username: email, password }) }),
  me: (t: string) => call<User>("/auth/me", {}, t),
};

export const lab = {
  scenarios: (t: string) => call<Scenario[]>("/sql-lab/scenarios", {}, t),
  run: (t: string, body: { scenario_ids?: string[]; mode: string; commit: boolean }) => call<RunResponse>("/sql-lab/run", json(body), t),
};
