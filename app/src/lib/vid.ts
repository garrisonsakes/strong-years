/**
 * L5: the sticky visitor id behind the $25/$30 price cell is signed, so a visitor
 * can't pick their price by editing the cookie. Web Crypto: runs in middleware too.
 */
const enc = new TextEncoder();

async function mac(id: string, secret: string): Promise<string> {
  const key = await crypto.subtle.importKey("raw", enc.encode(`vid:${secret}`), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = new Uint8Array(await crypto.subtle.sign("HMAC", key, enc.encode(id)));
  return [...sig.slice(0, 12)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export async function signVid(id: string, secret: string): Promise<string> {
  return `${id}.${await mac(id, secret)}`;
}

export async function verifyVid(value: string | undefined | null, secret: string): Promise<string | null> {
  if (!value || !secret) return null;
  const i = value.lastIndexOf(".");
  if (i <= 0) return null;
  const id = value.slice(0, i);
  const sig = value.slice(i + 1);
  const expected = await mac(id, secret);
  if (sig.length !== expected.length) return null;
  let diff = 0;
  for (let k = 0; k < sig.length; k++) diff |= sig.charCodeAt(k) ^ expected.charCodeAt(k);
  return diff === 0 ? id : null;
}
