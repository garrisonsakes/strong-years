import Link from "next/link";
import { requireEntitled } from "@/lib/auth/server";
import { kitchenWeek } from "@/lib/content";
import { kitchenPlan } from "@/lib/products";

export default async function Kitchen() {
  await requireEntitled();
  const now = new Date();
  const plan = kitchenPlan(now);
  const k = kitchenWeek(now); // Sun Yoon's weekly note + the honestly graded remedy
  return (
    <div className="space-y-8" data-testid="kitchen">
      <div>
        <h1 className="text-4xl">Sun Yoon&apos;s Kitchen</h1>
        <p className="mt-2 text-lg">This week: a breakfast, a main and a soup. Grams are per serving, from USDA data.</p>
        <blockquote className="card mt-4 bg-cream">
          <p className="font-display text-2xl italic">&ldquo;{k.sunMessage}&rdquo;</p>
          <p className="fine mt-2">— Sun Yoon (AI character)</p>
        </blockquote>
      </div>
      <section className="grid gap-6 lg:grid-cols-3">
        {plan.recipes.map((r) => (
          <article key={r.id} className="card" data-testid="recipe">
            <p className="font-bold">{r.category}</p>
            <h2 className="text-2xl">{r.name}</h2>
            {r.native && <p className="italic">{r.native}</p>}
            <ul className="mt-3 grid grid-cols-2 gap-2 text-[18px] font-bold" aria-label="Per serving">
              <li className="rounded-lg border-2 border-ink p-2">{Math.round(r.per_serving.protein_g)} g protein</li>
              <li className="rounded-lg border-2 border-ink p-2">{Math.round(r.per_serving.fiber_g)} g fiber</li>
              <li className="rounded-lg border-2 border-ink p-2">{Math.round(r.per_serving.kcal)} kcal</li>
              <li className="rounded-lg border-2 border-ink p-2">{Math.round(r.per_serving.sodium_mg)} mg sodium</li>
            </ul>
            <p className="mt-2">Serves {r.serves} · {r.minutes_active} min hands-on, {r.minutes_total} min total</p>
            <h3 className="mt-3 text-xl">You need</h3>
            <ul className="mt-1 list-disc space-y-1 pl-6">
              {r.ingredients.map((i) => (
                <li key={i.item}>
                  {i.amount} {i.item}
                  {i.grams > 0 && <span> ({i.grams} g)</span>}
                </li>
              ))}
            </ul>
            <h3 className="mt-3 text-xl">Do this</h3>
            <ol className="mt-1 list-decimal space-y-1 pl-6">
              {r.steps.map((st) => (
                <li key={st}>{st}</li>
              ))}
            </ol>
            {r.soft_food && (
              <p className="mt-3">
                <strong>Soft-food version:</strong> {r.soft_food}
              </p>
            )}
            {r.storage && (
              <p className="mt-2">
                <strong>Storage:</strong> {r.storage}
              </p>
            )}
            {r.cautions.length > 0 && (
              <div className="mt-3 rounded-lg bg-brass p-3 font-bold">
                <p>Who should skip or ask first:</p>
                <ul className="mt-1 space-y-1">
                  {r.cautions.map((c) => (
                    <li key={c}>{c.replace(/\s*\(E\d+\)/g, "")}</li>
                  ))}
                </ul>
              </div>
            )}
          </article>
        ))}
      </section>
      <section className="grid gap-6 lg:grid-cols-2">
        <div className="card">
          <h2 className="text-2xl">This week&apos;s grocery list</h2>
          <ul className="mt-3 space-y-1" data-testid="grocery-list">
            {plan.groceries.map((g) => (
              <li key={g.item} className="flex gap-2">
                <span aria-hidden="true">☐</span>
                <span>
                  {g.item} <span>({g.amounts.join(" + ")})</span>
                </span>
              </li>
            ))}
          </ul>
          <Link href="/app/printables/grocery-list" className="btn-outline mt-4">
            Print the list
          </Link>
        </div>
        <div className="card">
          <h2 className="text-2xl">This week&apos;s remedy, graded honestly</h2>
          <p className="mt-2 text-xl font-bold">{k.remedy.name}</p>
          <p className="mt-2 inline-block rounded-full bg-ink px-3 py-1 font-bold text-rice">Evidence: {k.remedy.grade}</p>
          <p className="mt-3">{k.remedy.note}</p>
          <p className="mt-3 font-bold">Who should skip or ask first: {k.remedy.skip}</p>
        </div>
      </section>
      <p className="fine">Recipes are general nutrition education, not medical advice. Kidney disease, diabetes or a special diet? Ask your doctor or dietitian how these fit.</p>
    </div>
  );
}
