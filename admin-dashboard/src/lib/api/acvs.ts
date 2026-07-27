/**
 * Centralised API client for the ACVS backend (FastAPI on port 8000).
 *
 * The Caddyfile gateway pattern lets us call any port via the
 * `XTransformPort` query param. We hide that detail behind a thin
 * wrapper so callers just use relative paths like `apiGet('/health')`.
 */
import { z } from "zod";

const BACKEND_PORT = 8000;

// ---------------------------------------------------------------------------
// Token storage (localStorage — fine for an admin dashboard SPA)
// ---------------------------------------------------------------------------
const ACCESS_KEY = "acvs.access_token";
const REFRESH_KEY = "acvs.refresh_token";
const USER_KEY = "acvs.user";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function setSession(access: string, refresh: string, user: User): void {
  localStorage.setItem(ACCESS_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Schemas
// ---------------------------------------------------------------------------
export const UserSchema = z.object({
  id: z.number(),
  email: z.string(),
  full_name: z.string(),
  role: z.enum(["user", "admin"]),
  is_active: z.boolean(),
});
export type User = z.infer<typeof UserSchema>;

export const TokenPairSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string(),
  user: UserSchema,
});
export type TokenPair = z.infer<typeof TokenPairSchema>;

export const ScanOutSchema = z.object({
  id: z.number(),
  modality: z.enum(["text", "image", "audio", "video", "fake_news"]),
  status: z.enum(["pending", "completed", "failed"]),
  confidence: z.number().nullable(),
  label: z.string().nullable(),
  explanation: z.string().nullable(),
  result: z.any().nullable(),
  created_at: z.string(),
  completed_at: z.string().nullable(),
  duration_ms: z.number().nullable(),
});
export type ScanOut = z.infer<typeof ScanOutSchema>;

export const ScanListSchema = z.object({
  items: z.array(ScanOutSchema),
  total: z.number(),
  page: z.number(),
  page_size: z.number(),
});
export type ScanList = z.infer<typeof ScanListSchema>;

// ---------------------------------------------------------------------------
// Core fetch wrapper
// ---------------------------------------------------------------------------
async function apiFetch<T>(
  path: string,
  opts: RequestInit = {},
  schema?: z.ZodSchema<T>,
): Promise<T> {
  const url = path.includes("?")
    ? `${path}&XTransformPort=${BACKEND_PORT}`
    : `${path}?XTransformPort=${BACKEND_PORT}`;

  const headers: Record<string, string> = {
    ...(opts.headers as Record<string, string>),
  };
  if (headers["Content-Type"] === undefined && !(opts.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  const token = getAccessToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(url, { ...opts, headers });
  if (res.status === 401) {
    // Try refresh once
    const refreshed = await tryRefresh();
    if (refreshed) {
      const retryHeaders = { ...headers, Authorization: `Bearer ${getAccessToken()}` };
      const retry = await fetch(url, { ...opts, headers: retryHeaders });
      if (!retry.ok) throw new ApiError(retry.status, await safeText(retry));
      return schema ? schema.parse(await retry.json()) : (await retry.json()) as T;
    }
    clearSession();
    throw new ApiError(401, "Session expired");
  }
  if (!res.ok) throw new ApiError(res.status, await safeText(res));
  const data = await res.json();
  return schema ? schema.parse(data) : (data as T);
}

async function safeText(res: Response): Promise<string> {
  try {
    return await res.text();
  } catch {
    return res.statusText;
  }
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// ---------------------------------------------------------------------------
// Refresh flow
// ---------------------------------------------------------------------------
let refreshing: Promise<boolean> | null = null;
async function tryRefresh(): Promise<boolean> {
  if (refreshing) return refreshing;
  const refresh = getRefreshToken();
  if (!refresh) return false;
  refreshing = (async () => {
    try {
      const res = await fetch(`/api/v1/auth/refresh?XTransformPort=${BACKEND_PORT}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (!res.ok) return false;
      const data = TokenPairSchema.parse(await res.json());
      setSession(data.access_token, data.refresh_token, data.user);
      return true;
    } catch {
      return false;
    } finally {
      refreshing = null;
    }
  })();
  return refreshing;
}

// ---------------------------------------------------------------------------
// Public API surface
// ---------------------------------------------------------------------------
export const api = {
  // Auth
  async register(email: string, full_name: string, password: string): Promise<TokenPair> {
    return apiFetch(
      "/api/v1/auth/register",
      { method: "POST", body: JSON.stringify({ email, full_name, password }) },
      TokenPairSchema,
    );
  },
  async login(email: string, password: string): Promise<TokenPair> {
    return apiFetch(
      "/api/v1/auth/login",
      { method: "POST", body: JSON.stringify({ email, password }) },
      TokenPairSchema,
    );
  },
  async me(): Promise<User> {
    return apiFetch("/api/v1/auth/me", {}, UserSchema);
  },

  // Scans
  async scanText(text: string): Promise<ScanOut> {
    return apiFetch(
      "/api/v1/scan/text",
      { method: "POST", body: JSON.stringify({ text }) },
      ScanOutSchema,
    );
  },
  async scanFakeNews(text: string, title?: string): Promise<ScanOut> {
    return apiFetch(
      "/api/v1/scan/fake-news",
      { method: "POST", body: JSON.stringify({ text, title }) },
      ScanOutSchema,
    );
  },
  async scanImage(file: File): Promise<ScanOut> {
    const fd = new FormData();
    fd.append("file", file);
    return apiFetch("/api/v1/scan/image", { method: "POST", body: fd }, ScanOutSchema);
  },
  async scanAudio(file: File): Promise<ScanOut> {
    const fd = new FormData();
    fd.append("file", file);
    return apiFetch("/api/v1/scan/audio", { method: "POST", body: fd }, ScanOutSchema);
  },
  async scanVideo(file: File): Promise<ScanOut> {
    const fd = new FormData();
    fd.append("file", file);
    return apiFetch("/api/v1/scan/video", { method: "POST", body: fd }, ScanOutSchema);
  },
  async history(params: { modality?: string; page?: number; page_size?: number } = {}): Promise<ScanList> {
    const q = new URLSearchParams();
    if (params.modality) q.set("modality", params.modality);
    q.set("page", String(params.page ?? 1));
    q.set("page_size", String(params.page_size ?? 20));
    return apiFetch(`/api/v1/scan/history?${q.toString()}`, {}, ScanListSchema);
  },
  async scanDetail(id: number): Promise<ScanOut> {
    return apiFetch(`/api/v1/scan/history/${id}`, {}, ScanOutSchema);
  },

  // Admin
  async adminStats(): Promise<AdminStats> {
    return apiFetch("/api/v1/admin/stats");
  },
  async adminUsers(page = 1, page_size = 20): Promise<AdminUserList> {
    return apiFetch(`/api/v1/admin/users?page=${page}&page_size=${page_size}`);
  },
  async toggleUserActive(user_id: number): Promise<{ id: number; is_active: boolean }> {
    return apiFetch(`/api/v1/admin/users/${user_id}/toggle-active`, { method: "POST" });
  },
  async promoteUser(user_id: number): Promise<{ id: number; role: string }> {
    return apiFetch(`/api/v1/admin/users/${user_id}/promote`, { method: "POST" });
  },
};

// ---------------------------------------------------------------------------
// Admin types (loose — backend returns plain JSON)
// ---------------------------------------------------------------------------
export interface AdminStats {
  users: { total: number };
  scans: {
    total: number;
    completed: number;
    failed: number;
    by_modality: Record<string, number>;
    by_label: Record<string, number>;
    avg_confidence: Record<string, number>;
  };
}

export interface AdminUserList {
  items: Array<{
    id: number;
    email: string;
    full_name: string;
    role: string;
    is_active: boolean;
    created_at: string;
    last_login_at: string | null;
  }>;
  total: number;
  page: number;
  page_size: number;
}
