"use client";
import { useEffect } from "react";

/** Logs one price-test exposure per browser; the server reads the cell from the sticky cookie. */
export function ExposureBeacon() {
  useEffect(() => {
    try {
      if (localStorage.getItem("sy_exposed")) return;
      localStorage.setItem("sy_exposed", "1");
    } catch {
      /* storage blocked: still log */
    }
    void fetch("/api/events", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: "price_cell_exposure" }), keepalive: true }).catch(() => undefined);
  }, []);
  return null;
}
