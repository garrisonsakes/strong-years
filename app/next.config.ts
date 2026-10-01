import type { NextConfig } from "next";

const CSP = [
  "default-src 'self'",
  `script-src 'self' 'unsafe-inline'${process.env.NODE_ENV === "production" ? "" : " 'unsafe-eval'"}`,
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self' data:",
  "connect-src 'self'",
  "media-src 'self' blob: https:",
  "frame-src 'none'",
  "frame-ancestors 'none'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self' https://checkout.stripe.com https://billing.stripe.com",
].join("; ");

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // Paid PDFs are read from content/downloads at runtime (not public/): ship them with the route.
  outputFileTracingIncludes: { "/api/downloads/[file]": ["./content/downloads/**"], "/api/waitlist/bonus": ["./content/downloads/twelve_week_printable.pdf"] },
  // Meta-safe short paths for paid traffic (OFFER.md 2.6 / FUNNEL.md 1.5):
  // ads point at /q/a and /q/b so no condition-adjacent word ever appears in an ad URL.
  async rewrites() {
    return [
      { source: "/q/a", destination: "/quiz/strength-age" },
      { source: "/q/b", destination: "/quiz/gut-energy" },
    ];
  },
  async redirects() {
    return [
      { source: "/", destination: "/start", permanent: false },
      { source: "/account", destination: "/app/account", permanent: false },
    ];
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
          // L10: no third-party scripts, frames or connections. Next's inline bootstrap needs
          // 'unsafe-inline' for scripts until nonces are wired; eval only in dev.
          { key: "Content-Security-Policy", value: CSP },
          { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" },
        ],
      },
    ];
  },
};

export default nextConfig;
