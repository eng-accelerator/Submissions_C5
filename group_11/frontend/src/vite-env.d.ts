/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Supabase project URL (public, embedded at build time) */
  readonly VITE_SUPABASE_URL?: string
  /** Supabase anon key (public) */
  readonly VITE_SUPABASE_ANON_KEY?: string
  /**
   * FastAPI base URL, no trailing slash. Omit in dev to use `/api` + Vite proxy.
   * Required for production when the UI and API are on different origins (unless you same-host proxy).
   */
  readonly VITE_BACKEND_URL?: string
  /**
   * Canonical site origin for OAuth redirects (no path, no trailing slash).
   * Example: `https://app.yourdomain.com`. If unset, `window.location.origin` is used at runtime.
   */
  readonly VITE_SITE_URL?: string
  /** Path after origin for post-OAuth redirect. Default: `/report/get` */
  readonly VITE_OAUTH_REDIRECT_PATH?: string
  /** Dev only: FastAPI origin for the `/api` Vite proxy */
  readonly VITE_DEV_PROXY_TARGET?: string
  /** Dev server port (optional, default 5173) */
  readonly VITE_DEV_PORT?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
