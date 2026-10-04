// Central API configuration (env-driven).
// VITE_API_URL="" (default) -> relative "/api/..." : uses Vite proxy in dev,
// same-origin backend in prod. Set e.g. "http://localhost:8000" for direct calls.
// Bare hostnames (Render fromService `host`, e.g. "my-api.onrender.com") are
// upgraded to https:// automatically.

function normalizeBase(raw) {
  const v = (raw ?? "").trim().replace(/\/+$/, "");
  if (!v) return "";
  if (v.startsWith("/") || /^[a-zA-Z][a-zA-Z0-9+.-]*:\/\//.test(v)) return v;
  return `https://${v}`;
}

export const API_BASE_URL = normalizeBase(import.meta.env.VITE_API_URL);
export const BOUNDARY_URL = `${API_BASE_URL}/api/boundary`;
export const HEALTH_URL = `${API_BASE_URL}/api/health`;
