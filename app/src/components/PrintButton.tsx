"use client";

export function PrintButton({ label = "Print this page" }: { label?: string }) {
  return (
    <button type="button" className="btn-ink" onClick={() => window.print()}>
      {label}
    </button>
  );
}
