/**
 * Strength Age trend chart: one series (Jade 2px line, 8px+ markers, recessive grid,
 * Ink labels), with a hover tooltip per point via <title> and a table view for
 * screen readers and anyone who prefers numbers. Lower is better, so the y-axis is
 * labelled in plain words.
 */
export interface TrendPoint {
  label: string;
  value: number;
}

/**
 * L9: two drawings of the same chart. On phones the canvas is narrower, so the
 * labels render at about 18px on a 390px screen instead of shrinking to 11px.
 */
export function TrendChart({
  points,
  title,
  testId,
}: {
  points: TrendPoint[];
  title: string;
  testId?: string;
}) {
  if (points.length === 0)
    return (
      <p className="font-bold">
        No retests yet. Your first one takes 3 minutes.
      </p>
    );
  return (
    <figure data-testid={testId}>
      <figcaption className="mb-2 text-xl font-bold">{title}</figcaption>
      <div className="sm:hidden">
        <TrendSvg points={points} title={title} W={400} H={300} />
      </div>
      <div className="hidden sm:block">
        <TrendSvg points={points} title={title} W={640} H={340} />
      </div>
      <TrendTable points={points} />
    </figure>
  );
}

function TrendSvg({
  points,
  title,
  W,
  H,
}: {
  points: TrendPoint[];
  title: string;
  W: number;
  H: number;
}) {
  const small = W < 500;
  const pad = small
    ? { l: 56, r: 24, t: 44, b: 56 }
    : { l: 64, r: 40, t: 44, b: 60 };
  const values = points.map((p) => p.value);
  const lo = Math.min(...values);
  const hi = Math.max(...values);
  const step = Math.max(1, Math.ceil((hi - lo + 4) / 3));
  const min = Math.floor((lo - 2) / step) * step;
  const max = min + step * 3 >= hi + 1 ? min + step * 3 : min + step * 4;
  const x = (i: number) =>
    pad.l +
    (points.length === 1
      ? (W - pad.l - pad.r) / 2
      : (i * (W - pad.l - pad.r)) / (points.length - 1));
  const y = (v: number) =>
    pad.t + ((v - min) * (H - pad.t - pad.b)) / Math.max(1, max - min);
  const ticks: number[] = [];
  for (let t = min; t <= max; t += step) ticks.push(t);
  const path = points
    .map(
      (p, i) =>
        `${i === 0 ? "M" : "L"}${x(i).toFixed(1)},${y(p.value).toFixed(1)}`,
    )
    .join(" ");
  const last = points[points.length - 1]!;
  const anchor = (i: number) =>
    points.length === 1
      ? "middle"
      : i === 0
        ? "start"
        : i === points.length - 1
          ? "end"
          : "middle";
  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="h-auto w-full"
      role="img"
      aria-label={`${title}. ${points.map((p) => `${p.label}: ${p.value}`).join(", ")}.`}
    >
      {ticks.map((t) => (
        <g key={t}>
          <line
            x1={pad.l}
            x2={W - pad.r}
            y1={y(t)}
            y2={y(t)}
            stroke="#16120E"
            strokeOpacity="0.15"
            strokeWidth="1"
          />
          <text
            x={pad.l - 12}
            y={y(t) + 8}
            textAnchor="end"
            fontSize="22"
            fill="#16120E"
          >
            {t}
          </text>
        </g>
      ))}
      <text x={pad.l} y={24} fontSize="20" fill="#16120E" fontWeight="700">
        Younger strength age ↑
      </text>
      <path
        d={path}
        fill="none"
        stroke="#1F5A46"
        strokeWidth="3"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      {points.map((p, i) => (
        <g key={p.label + i}>
          <circle cx={x(i)} cy={y(p.value)} r="16" fill="transparent">
            <title>{`${p.label}: Strength Age ${p.value}`}</title>
          </circle>
          <circle
            cx={x(i)}
            cy={y(p.value)}
            r="8"
            fill="#1F5A46"
            stroke="#FFFFFF"
            strokeWidth="2"
            pointerEvents="none"
          />
          <text
            x={x(i)}
            y={H - 18}
            textAnchor={anchor(i)}
            fontSize="22"
            fill="#16120E"
          >
            {p.label}
          </text>
        </g>
      ))}
      <text
        x={x(points.length - 1) + (points.length > 1 ? -14 : 0)}
        y={y(last.value) - 16}
        textAnchor={points.length > 1 ? "end" : "middle"}
        fontSize="26"
        fontWeight="700"
        fill="#16120E"
      >
        {last.value}
      </text>
    </svg>
  );
}

function TrendTable({ points }: { points: TrendPoint[] }) {
  return (
    <details className="mt-2">
      <summary className="cursor-pointer font-bold underline">
        Show as a table
      </summary>
      <table className="mt-2 w-full border-collapse text-left">
        <thead>
          <tr>
            <th className="border-b-2 border-ink py-1">Month</th>
            <th className="border-b-2 border-ink py-1">Strength Age</th>
          </tr>
        </thead>
        <tbody>
          {points.map((p, i) => (
            <tr key={p.label + i}>
              <td className="border-b border-ink py-1">{p.label}</td>
              <td className="border-b border-ink py-1">{p.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </details>
  );
}

export function ExampleChart() {
  return (
    <div>
      <p className="mb-2 inline-block rounded-full bg-ink px-3 py-1 text-[16px] font-bold text-rice">
        Example
      </p>
      <TrendChart
        title="Example Strength Age over three monthly retests"
        points={[
          { label: "Month 1", value: 72 },
          { label: "Month 2", value: 70 },
          { label: "Month 3", value: 67 },
        ]}
      />
    </div>
  );
}
