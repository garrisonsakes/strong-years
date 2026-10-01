/** L1: what the login page may render from its query string. */
export const LOGIN_ERRORS: Record<string, string> = {
  expired: "That link has expired or was already used. We'll send a new one.",
  demo: "The demo member is missing. Restart the demo server.",
  code: "That code didn't work. Check the newest email from us, or ask for a new code.",
  busy: "Too many tries. Please wait a few minutes, then ask for a new code.",
  gift: "That gift link has expired or was already used. Enter your gift code again and we'll email a fresh link.",
};

export function loginError(code: string | undefined): string | null {
  return code ? (LOGIN_ERRORS[code] ?? LOGIN_ERRORS.expired!) : null;
}

/** Only the in-memory demo shows the link, and only one pointing at our own verify route. */
export function loginDemoLink(raw: string | undefined, opts: { mockDb: boolean; siteUrl: string }): string | null {
  return opts.mockDb && raw && raw.startsWith(`${opts.siteUrl}/auth/verify?`) ? raw : null;
}

/** Remembers which address a sign-in code was sent to (httpOnly, 30 minutes). */
export const LOGIN_EMAIL_COOKIE = "sy_login_email";
