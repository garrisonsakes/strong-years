import { createHmac, timingSafeEqual } from "node:crypto";

/** Twilio request signature (HMAC-SHA1 of URL + sorted params), compared in constant time. */
export function validTwilioSignature(url: string, params: URLSearchParams, header: string | null, token: string) {
  if (!header) return false;
  const data = url + [...params.keys()].sort().map((k) => k + (params.get(k) ?? "")).join("");
  const expected = createHmac("sha1", token).update(data).digest("base64");
  const a = Buffer.from(expected);
  const b = Buffer.from(header);
  return a.length === b.length && timingSafeEqual(a, b);
}
