// API base URL: same-origin by default (vite proxies /api to the backend).
// The absolute backend URL is used ONLY inside the Tauri WebView, where there
// is no same-origin dev server. Browser tabs on LAN/Tailscale hostnames must
// never use a hardcoded localhost URL (CORS + wrong-host failure class).
declare global {
  interface Window {
    __TAURI__?: unknown;
    __TAURI_INTERNALS__?: unknown;
  }
}

function isTauri(): boolean {
  if (typeof window === "undefined") return false;
  return Boolean(window.__TAURI__ || window.__TAURI_INTERNALS__);
}

export const API_BASE = isTauri() ? "http://127.0.0.1:10863" : "";
