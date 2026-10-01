/**
 * Round 8 (AUDIT_FINAL §7): the client IP comes only from headers a trusted proxy
 * wrote. A client can put anything in X-Forwarded-For, so the leftmost entry is
 * never trusted on its own. Edge-safe (used by middleware).
 *
 *   On Vercel (VERCEL=1): x-real-ip / x-vercel-forwarded-for, which Vercel's edge
 *     sets and overwrites (clients can't spoof them).
 *   TRUSTED_PROXY_HOPS=N: the Nth entry from the right of X-Forwarded-For (each of
 *     our N proxies appends one entry; anything the client prepended is ignored).
 *   TRUSTED_PROXIES=ip,ip: walk X-Forwarded-For from the right, skipping our
 *     proxies; the first address that isn't ours is the client.
 *   CLIENT_IP_HEADER / TRUST_CLOUDFLARE, or auto-detected Fly / Netlify: that
 *     platform's own client-IP header; Render / Railway / Heroku / Cloud Run: one hop.
 *   Otherwise: proxy headers are not trusted ("unknown"); see rateLimitKey().
 */
type HeaderBag = { get(name: string): string | null };

export interface TrustConfig {
  vercel: boolean;
  hops: number;
  proxies: string[];
  /** A single header the hosting platform's edge sets and overwrites (Fly, Netlify, Cloudflare). */
  platformHeader?: string | null;
}

/**
 * Round 9: works on any host. Explicit settings win; otherwise the platform is
 * detected from the env vars it sets, and its own client-IP header (or its one
 * proxy hop) is used.
 */
export function trustConfigFromEnv(e: Record<string, string | undefined> = process.env): TrustConfig {
  const explicitHops = Number(e.TRUSTED_PROXY_HOPS ?? 0);
  const proxies = (e.TRUSTED_PROXIES ?? "").split(",").map((s) => s.trim()).filter(Boolean);
  const platformHeader =
    e.CLIENT_IP_HEADER?.toLowerCase() ||
    (e.TRUST_CLOUDFLARE === "true" ? "cf-connecting-ip" : null) ||
    (e.FLY_APP_NAME ? "fly-client-ip" : null) ||
    (e.NETLIFY === "true" ? "x-nf-client-connection-ip" : null);
  // Render, Railway, Heroku and Cloud Run each put exactly one proxy in front that appends to X-Forwarded-For.
  const oneHopPlatform = Boolean(e.RENDER || e.RAILWAY_ENVIRONMENT || e.DYNO || e.K_SERVICE);
  const hops = Number.isInteger(explicitHops) && explicitHops > 0 && explicitHops < 10 ? explicitHops : oneHopPlatform ? 1 : 0;
  return { vercel: e.VERCEL === "1", hops, proxies, platformHeader };
}

/** True when this host has some trusted way to know the client IP. */
export function clientIpTrustConfigured(cfg: TrustConfig = trustConfigFromEnv()): boolean {
  return cfg.vercel || cfg.hops > 0 || cfg.proxies.length > 0 || Boolean(cfg.platformHeader);
}

const IP_RE = /^[0-9a-fA-F:.]{2,45}$/;
const clean = (s: string | null | undefined) => {
  const v = (s ?? "").trim();
  return IP_RE.test(v) ? v : null;
};

export function trustedClientIp(h: HeaderBag, cfg: TrustConfig = trustConfigFromEnv()): string {
  if (cfg.vercel) {
    const v = clean(h.get("x-real-ip")) ?? clean(h.get("x-vercel-forwarded-for")?.split(",")[0]);
    if (v) return v;
  }
  if (cfg.platformHeader) {
    const v = clean(h.get(cfg.platformHeader)?.split(",")[0]);
    if (v) return v;
  }
  const chain = (h.get("x-forwarded-for") ?? "").split(",").map((s) => s.trim()).filter(Boolean);
  if (cfg.proxies.length) {
    for (let i = chain.length - 1; i >= 0; i--) {
      if (!cfg.proxies.includes(chain[i]!)) return clean(chain[i]) ?? "unknown";
    }
    return "unknown";
  }
  if (cfg.hops > 0) return clean(chain[chain.length - cfg.hops]) ?? "unknown";
  return "unknown";
}

/**
 * Round 9: the key rate limits use. The trusted IP whenever the host gives us one.
 * Only if it can't (no proxy configured or detected) do limits fall back to the
 * client-supplied address, so visitors don't all share one bucket; that fallback can
 * be spoofed to dodge a limit, never to lock anyone else out. The admin lockout never
 * uses it (trusted IP + username only).
 */
export function rateLimitKey(h: HeaderBag, cfg: TrustConfig = trustConfigFromEnv()): string {
  const trusted = trustedClientIp(h, cfg);
  if (trusted !== "unknown") return trusted;
  const claimed = clean(h.get("x-forwarded-for")?.split(",")[0]) ?? clean(h.get("x-real-ip"));
  return claimed ? `untrusted:${claimed}` : "unknown";
}
