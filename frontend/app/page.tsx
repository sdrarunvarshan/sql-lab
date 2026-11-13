"use client";
import { useEffect, useMemo, useState } from "react";
import { API, TOOLS, auth, lab, RunResult, Scenario, User } from "../lib/api";

const LEVELS = ["beginner", "intermediate", "advanced", "professional"];

function Auth({ onToken }: { onToken: (t: string) => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [f, setF] = useState({ email: "", name: "", password: "" });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true); setErr("");
    try {
      if (mode === "register") await auth.register(f.email, f.name, f.password);
      onToken((await auth.login(f.email, f.password)).access_token);
    } catch (x) { setErr((x as Error).message); }
    setBusy(false);
  }
  return (
    <form className="auth" onSubmit={submit}>
      <h1>SQL Lab</h1>
      <p>{mode === "login" ? "Sign in to run SQL scenarios." : "Create an account (password: 8+ characters)."}</p>
      <input type="email" required placeholder="Email" autoComplete="email" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} />
      {mode === "register" && <input type="text" required minLength={2} placeholder="Full name" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />}
      <input type="password" required minLength={8} maxLength={72} placeholder="Password" autoComplete={mode === "login" ? "current-password" : "new-password"} value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} />
      {err && <div className="err" role="alert">{err}</div>}
      <button className="btn" disabled={busy}>{mode === "login" ? "Sign in" : "Create account"}</button>
      <button type="button" className="btn ghost" onClick={() => setMode(mode === "login" ? "register" : "login")}>
        {mode === "login" ? "Create an account" : "I already have an account"}
      </button>
    </form>
  );
}

function ResultTable({ cols, rows }: { cols: string[]; rows: unknown[][] }) {
  return (
    <div className="scroll"><table>
      <thead><tr>{cols.map((c) => <th key={c}>{c}</th>)}</tr></thead>
      <tbody>{rows.map((r, i) => <tr key={i}>{r.map((v, j) => <td key={j}>{v === null ? "NULL" : typeof v === "object" ? JSON.stringify(v) : String(v)}</td>)}</tr>)}</tbody>
    </table></div>
  );
}

export default function Home() {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [sel, setSel] = useState<string>("");
  const [results, setResults] = useState<Record<string, RunResult>>({});
  const [level, setLevel] = useState("all");
  const [q, setQ] = useState("");
  const [mode, setMode] = useState("temporal");
  const [commit, setCommit] = useState(false);
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<{ text: string; bad?: boolean; wf?: string | null } | null>(null);

  useEffect(() => { setToken(localStorage.getItem("token")); }, []);
  const logout = () => { localStorage.removeItem("token"); setToken(null); setUser(null); setResults({}); };

  useEffect(() => {
    if (!token) return;
    localStorage.setItem("token", token);
    Promise.all([auth.me(token), lab.scenarios(token)])
      .then(([u, s]) => { setUser(u); setScenarios(s); setSel((c) => c || s[0]?.id || ""); })
      .catch(logout);
  }, [token]);

  const shown = useMemo(
    () => scenarios.filter((s) => (level === "all" || s.level === level) && (s.title + s.category + s.id).toLowerCase().includes(q.toLowerCase())),
    [scenarios, level, q]);
  const groups = useMemo(() => {
    const m = new Map<string, Scenario[]>();
    shown.forEach((s) => m.set(s.category, [...(m.get(s.category) ?? []), s]));
    return [...m.entries()];
  }, [shown]);
  const current = scenarios.find((s) => s.id === sel);
  const res = results[sel];

  async function run(ids?: string[]) {
    if (!token) return;
    setBusy(true); setNote(null);
    try {
      const out = await lab.run(token, { scenario_ids: ids, mode, commit });
      setResults((r) => ({ ...r, ...Object.fromEntries(out.results.map((x) => [x.scenario_id, x])) }));
      const { ok, failed, total } = out.summary;
      setNote({ text: `${ok} of ${total} scenarios succeeded${failed ? `, ${failed} failed` : ""}.`, bad: failed > 0, wf: out.workflow_id });
    } catch (x) {
      if ((x as { status?: number }).status === 401) return logout();
      setNote({ text: (x as Error).message, bad: true });
    }
    setBusy(false);
  }

  if (!token) return <Auth onToken={setToken} />;

  return (
    <>
      <header className="top">
        <h1>SQL Lab</h1>
        <nav aria-label="Observability tools">
          <a href={TOOLS.jaeger} target="_blank" rel="noreferrer">Traces (Jaeger)</a>
          <a href={TOOLS.temporal} target="_blank" rel="noreferrer">Workflows (Temporal)</a>
          <a href={TOOLS.prometheus} target="_blank" rel="noreferrer">Metrics</a>
          <a href={TOOLS.docs} target="_blank" rel="noreferrer">REST docs</a>
        </nav>
        <span className="who">{user?.email} ({user?.role})</span>
        <button className="btn ghost" onClick={logout}>Sign out</button>
      </header>
      <div className="shell">
        <aside className="side">
          <div className="filters">
            <input type="text" placeholder="Search scenarios" aria-label="Search scenarios" value={q} onChange={(e) => setQ(e.target.value)} />
            <select aria-label="Level" value={level} onChange={(e) => setLevel(e.target.value)}>
              <option value="all">All levels</option>
              {LEVELS.map((l) => <option key={l}>{l}</option>)}
            </select>
          </div>
          {groups.length === 0 && <p className="meta">No scenarios match. Clear the search or pick another level.</p>}
          {groups.map(([cat, items]) => (
            <section key={cat}>
              <h3>{cat}</h3>
              {items.map((s) => (
                <button key={s.id} className="item" aria-current={s.id === sel} onClick={() => setSel(s.id)}>
                  <span className={`dot ${results[s.id]?.status ?? ""}`} aria-hidden />
                  <span>{s.title}</span><span className="lvl">{s.level}</span>
                </button>
              ))}
            </section>
          ))}
        </aside>
        <main className="main">
          <div className="bar">
            <select aria-label="Execution mode" value={mode} onChange={(e) => setMode(e.target.value)}>
              <option value="temporal">Run through Temporal</option>
              <option value="direct">Run directly</option>
            </select>
            {user?.role === "admin" && (
              <label><input type="checkbox" checked={commit} onChange={(e) => setCommit(e.target.checked)} /> Keep changes (commit)</label>
            )}
            <button className="btn" disabled={busy || !current} onClick={() => run([sel])}>Run scenario</button>
            <button className="btn ghost" disabled={busy} onClick={() => run(undefined)}>Run all {scenarios.length} scenarios</button>
          </div>
          {note && (
            <div className="summary" role="status" style={{ color: note.bad ? "var(--bad)" : "var(--ok)" }}>
              {note.text}{" "}
              {note.wf && <a href={`${TOOLS.temporal}/namespaces/default/workflows/${note.wf}`} target="_blank" rel="noreferrer">Open workflow</a>}
            </div>
          )}
          {current && (
            <>
              <h2 style={{ marginBottom: 2 }}>{current.title}</h2>
              <div className="meta">{current.category}, {current.level}. Changes are rolled back unless you keep them.</div>
              {res?.status === "failed" && <div className="err" role="alert">Failed: {res.error}</div>}
              {current.steps.map((sql, i) => {
                const r = res?.steps.find((s) => s.step === i + 1);
                return (
                  <div className="step" key={i}>
                    <pre>{sql}</pre>
                    {r && <div className="meta">{r.command}, {r.rowcount} row(s), {r.ms} ms</div>}
                    {r && r.columns.length > 0 && <ResultTable cols={r.columns} rows={r.rows} />}
                  </div>
                );
              })}
            </>
          )}
        </main>
      </div>
    </>
  );
}
