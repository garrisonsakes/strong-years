import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return { rules: [{ userAgent: "*", allow: ["/start", "/gift", "/reset", "/kitchen", "/how-we-make-this"], disallow: ["/app", "/admin", "/api", "/checkout", "/upsell", "/quiz/strength-age/result", "/quiz/gut-energy/result"] }] };
}
