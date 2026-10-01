import type { ReactNode } from "react";

export interface LegalSection {
  id?: string;
  heading: string;
  body: ReactNode;
}

/**
 * Shared layout for the policy pages. Every one of them is a working draft
 * written from the product's actual behaviour; none has been reviewed by a lawyer.
 */
export function LegalPage({ title, intro, updated, sections, children }: { title: string; intro?: ReactNode; updated: string; sections: LegalSection[]; children?: ReactNode }) {
  return (
    <div className="narrow space-y-8 py-12">
      <p role="note" className="rounded-xl border-4 border-persimmon bg-rice p-4 text-xl font-bold text-ink" data-testid="legal-draft">
        DRAFT: attorney review required. This page describes how Strong Years works today, but it has not yet been reviewed by a lawyer and may change.
      </p>
      <header className="space-y-3">
        <h1 className="text-4xl">{title}</h1>
        <p className="font-bold">Last updated: {updated}</p>
        {intro && <div className="text-lg">{intro}</div>}
      </header>
      {children}
      <nav aria-label="On this page" className="card">
        <p className="font-bold">On this page</p>
        <ol className="mt-2 list-decimal space-y-1 pl-6">
          {sections.map((s, i) => (
            <li key={s.heading}>
              <a href={`#${s.id ?? `s${i + 1}`}`} className="font-bold text-ink underline">
                {s.heading}
              </a>
            </li>
          ))}
        </ol>
      </nav>
      {sections.map((s, i) => (
        <section key={s.heading} id={s.id ?? `s${i + 1}`} className="space-y-3">
          <h2 className="text-3xl">
            {i + 1}. {s.heading}
          </h2>
          <div className="space-y-3 text-[20px]">{s.body}</div>
        </section>
      ))}
    </div>
  );
}

export const LEGAL_UPDATED = "September 30, 2026";
