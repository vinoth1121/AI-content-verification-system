import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";

interface User {
  full_name: string;
  email: string;
  role: string;
}

interface ScanResult {
  id: number;
  modality: string;
  label: string | null;
  confidence: number | null;
  explanation: string | null;
}

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [email, setEmail] = useState("admin@acvs.io");
  const [password, setPassword] = useState("Admin123!Admin");
  const [text, setText] = useState("");
  const [result, setResult] = useState<ScanResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function login() {
    setBusy(true); setError(null);
    try {
      const res = await invoke<any>("login", { payload: { email, password } });
      setUser(res.user);
    } catch (e: any) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function scan() {
    setBusy(true); setError(null);
    try {
      const res = await invoke<any>("scan_text", { payload: { text } });
      setResult(res);
    } catch (e: any) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  if (!user) {
    return (
      <div style={wrap}>
        <div style={card}>
          <h1 style={h1}>ACVS Desktop</h1>
          <input style={input} value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
          <input style={input} type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
          <button style={btn} onClick={login} disabled={busy}>{busy ? "…" : "Sign in"}</button>
          {error && <p style={{ color: "#f43f5e", fontSize: 12 }}>{error}</p>}
        </div>
      </div>
    );
  }

  return (
    <div style={{ ...wrap, alignItems: "flex-start", padding: 32 }}>
      <div style={{ width: "100%", maxWidth: 720 }}>
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
          <h1 style={h1}>ACVS</h1>
          <span style={{ color: "#6b7280", fontSize: 13 }}>Signed in as {user.full_name}</span>
        </header>

        <h2 style={h2}>Text detection</h2>
        <textarea style={{ ...input, height: 120, resize: "vertical" }} value={text} onChange={(e) => setText(e.target.value)} placeholder="Paste text to verify…" />
        <button style={btn} onClick={scan} disabled={busy || !text.trim()}>{busy ? "Scanning…" : "Detect"}</button>

        {result && (
          <div style={{ ...card, marginTop: 16, textAlign: "left" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
              <strong style={{ textTransform: "capitalize", color: result.label === "deepfake" ? "#f43f5e" : result.label === "human" ? "#10b981" : "#f59e0b" }}>
                {result.label?.replace(/_/g, " ")}
              </strong>
              <span>{result.confidence != null ? `${Math.round(result.confidence * 100)}%` : "—"}</span>
            </div>
            <p style={{ color: "#4b5563", fontSize: 13 }}>{result.explanation}</p>
          </div>
        )}
        {error && <p style={{ color: "#f43f5e", fontSize: 12 }}>{error}</p>}
      </div>
    </div>
  );
}

const wrap: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  minHeight: "100vh",
  background: "#f8fafc",
  fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  color: "#111",
};

const card: React.CSSProperties = {
  background: "#fff",
  padding: 24,
  borderRadius: 12,
  boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
  width: 320,
  textAlign: "center",
};

const h1: React.CSSProperties = { fontSize: 22, margin: "0 0 16px" };
const h2: React.CSSProperties = { fontSize: 14, color: "#6b7280", margin: "16px 0 8px", textTransform: "uppercase", letterSpacing: 0.5 };

const input: React.CSSProperties = {
  width: "100%",
  padding: 8,
  marginBottom: 8,
  border: "1px solid #d1d5db",
  borderRadius: 6,
  fontSize: 13,
  boxSizing: "border-box",
};

const btn: React.CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  background: "#10b981",
  color: "#fff",
  border: 0,
  borderRadius: 6,
  fontSize: 13,
  cursor: "pointer",
  marginTop: 4,
};
