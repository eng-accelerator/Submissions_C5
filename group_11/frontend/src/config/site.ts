/**
 * URLs derived from env + runtime. Used for OAuth redirects in production
 * where the canonical origin must match Supabase redirect allowlist.
 */
export function getSiteOrigin(): string {
  const fromEnv = import.meta.env.VITE_SITE_URL?.trim()
  if (fromEnv) {
    return fromEnv.replace(/\/$/, '')
  }
  if (typeof window !== 'undefined') {
    return window.location.origin
  }
  return ''
}

export function getOAuthRedirectUrl(): string {
  const pathRaw = import.meta.env.VITE_OAUTH_REDIRECT_PATH?.trim() || '/report/get'
  const path = pathRaw.startsWith('/') ? pathRaw : `/${pathRaw}`
  return `${getSiteOrigin()}${path}`
}
