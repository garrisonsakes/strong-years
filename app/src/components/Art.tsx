/**
 * Labelled illustration placeholders. These are deliberately drawn, not photographic,
 * and always carry the words "AI character" so nobody can mistake them for a real
 * person (SAFETY_RULES.md T-01, V-06). Swap in the reference-locked character stills
 * from CHARACTERS.md §13 when they exist; keep the label.
 */
export function CharacterArt({ who, className = "" }: { who: "chang" | "sun" | "both"; className?: string }) {
  const label = who === "chang" ? "Chang Yin, 74" : who === "sun" ? "Sun Yoon, 76" : "Chang Yin & Sun Yoon";
  const scene = who === "chang" ? "Garage gym: chair against the wall, kettlebells" : who === "sun" ? "Kitchen: stove, onggi crocks, steam" : "Kitchen table, barley tea";
  return (
    <figure className={`relative h-fit self-start overflow-hidden rounded-2xl border-2 border-ink ${className}`}>
      <svg viewBox="0 0 400 300" role="img" aria-label={`Illustration placeholder: ${label}, an AI character. ${scene}.`} className="block h-auto w-full">
        <rect width="400" height="300" fill={who === "sun" ? "#F3E9D6" : "#DDEBE3"} />
        {who !== "sun" && (
          <g>
            <rect x="0" y="230" width="400" height="70" fill="#16120E" opacity="0.9" />
            <rect x="40" y="120" width="70" height="10" rx="3" fill="#16120E" />
            <rect x="46" y="130" width="8" height="100" fill="#16120E" />
            <rect x="96" y="130" width="8" height="100" fill="#16120E" />
            <rect x="40" y="170" width="70" height="8" fill="#16120E" />
            <circle cx="300" cy="218" r="16" fill="#1F5A46" stroke="#16120E" strokeWidth="4" />
            <circle cx="345" cy="222" r="12" fill="#B3311C" stroke="#16120E" strokeWidth="4" />
          </g>
        )}
        {who !== "chang" && (
          <g>
            <rect x={who === "both" ? 250 : 40} y="150" width="120" height="16" rx="4" fill="#16120E" />
            <rect x={who === "both" ? 270 : 60} y="110" width="80" height="44" rx="10" fill="#B3311C" stroke="#16120E" strokeWidth="4" />
            <path d={who === "both" ? "M290 100 q8 -18 0 -36 M310 100 q8 -18 0 -36" : "M80 100 q8 -18 0 -36 M100 100 q8 -18 0 -36"} stroke="#16120E" strokeWidth="4" fill="none" strokeLinecap="round" />
            <ellipse cx={who === "both" ? 120 : 300} cy="200" rx="34" ry="44" fill="#8E5A2B" stroke="#16120E" strokeWidth="4" />
          </g>
        )}
        <g>
          <circle cx={who === "sun" ? 230 : 200} cy="92" r="30" fill="#E7B85A" stroke="#16120E" strokeWidth="4" />
          <path d={who === "sun" ? "M180 230 q50 -120 100 0 z" : "M150 230 q50 -120 100 0 z"} fill="#1F5A46" stroke="#16120E" strokeWidth="4" />
        </g>
      </svg>
      <figcaption className="absolute left-3 top-3 rounded-full bg-ink px-3 py-1 text-[16px] font-bold text-rice">
        AI character · illustration placeholder
      </figcaption>
      <p className="border-t-2 border-ink bg-rice px-4 py-2 text-fine font-bold">{label}</p>
    </figure>
  );
}

/** Product-led hero: the actual session screen, drawn in HTML (not a stock photo). */
export function PhoneSession() {
  return (
    <div className="mx-auto w-[300px] max-w-full flex-none rounded-[40px] border-[10px] sm:mx-0 border-ink bg-ink shadow-[8px_8px_0_#1F5A46]" aria-label="Example of the Daily Practice screen">
      <div className="overflow-hidden rounded-[30px] bg-rice">
        <div className="relative bg-jade p-4 text-rice">
          <span className="rounded-full bg-ink px-3 py-1 text-[18px] font-bold text-rice">AI character</span>
          <div className="mt-6 flex items-end justify-between">
            <div>
              <p className="text-[16px] font-bold text-rice">Monday · Strength</p>
              <p className="font-display text-[28px] leading-tight text-rice">Sit-to-stand</p>
            </div>
            <p className="font-display text-[40px] leading-none text-rice">6/10</p>
          </div>
          <p className="mt-2 text-[16px] text-rice">&ldquo;Breathe out as you stand.&rdquo;</p>
        </div>
        <div className="space-y-3 p-4">
          <div className="grid grid-cols-4 gap-1 text-center text-[14px] font-bold">
            {["Rebuild", "Steady", "Strong", "Iron"].map((t) => (
              <span key={t} className={`rounded-md border-2 border-ink py-1 ${t === "Steady" ? "bg-ink text-rice" : "bg-rice text-ink"}`}>
                {t}
              </span>
            ))}
          </div>
          <div className="rounded-xl border-2 border-ink p-3 text-[16px] font-bold">Sore knee today? Tap to swap.</div>
          <div className="flex h-14 items-center justify-center rounded-xl bg-persimmon text-[20px] font-bold text-rice">Pause</div>
        </div>
      </div>
    </div>
  );
}

export function ExampleStrengthCard() {
  return (
    <div className="w-[260px] max-w-full rotate-[-2deg] rounded-xl border-2 border-ink bg-rice p-4 shadow-[6px_6px_0_#16120E]">
      <p className="text-[16px] font-bold">Example card</p>
      <p className="font-display text-[22px]">Strength Age</p>
      <p className="font-display text-[40px] leading-none">
        68 <span aria-hidden="true">→</span> <span className="text-persimmon">64</span>
      </p>
      <p className="mt-1 text-[16px]">After 3 months of retests</p>
      <div className="mt-2 h-2 w-full bg-brass" aria-hidden="true" />
    </div>
  );
}
