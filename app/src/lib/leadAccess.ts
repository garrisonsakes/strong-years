/** M12: quiz result pages are reachable by link for 60 days, then they're gone. */
export const LEAD_RESULT_DAYS = 60;

export function leadResultExpired(lead: { created_at: string }, now = Date.now()): boolean {
  return now - new Date(lead.created_at).getTime() > LEAD_RESULT_DAYS * 86_400_000;
}
