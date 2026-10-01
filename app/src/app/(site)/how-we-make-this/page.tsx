import type { Metadata } from "next";
import { copy } from "@/lib/copy";

export const metadata: Metadata = { title: "How we make this" };

const GUIDES = [
  ["CDC STEADI", "The CDC's older-adult assessment protocols we use for the quiz and retests: the 30-second chair stand and the 4-stage balance test."],
  ["Rikli & Jones, Senior Fitness Test", "Published norms for the chair stand, arm curl, 2-minute step, sit-and-reach and up-and-go tests. Strength Age compares you with these."],
  ["ACSM guidance for older adults", "Progressive strength, balance and aerobic activity guidance for adults 65+."],
  ["Sherrington et al., Cochrane Review 2019", "A review of balance and strength exercise programs for older adults, which shaped how our balance sessions progress."],
  ["PROT-AGE study group", "Protein recommendations for older adults: 1.0–1.2 g per kg of body weight a day for most healthy older adults."],
  ["Dietary fiber guidance for adults over 50", "About 21 g a day for women and 30 g for men."],
];

export default function HowWeMakeThis() {
  return (
    <div className="narrow py-12">
      <h1 className="text-4xl">How we make this</h1>
      <p className="mt-5 text-lg">{copy.disclosureBlock}</p>
      <h2 className="mt-10 text-3xl">Who makes Chang Yin and Sun Yoon</h2>
      <p className="mt-3">
        A small team of people writes every session, every recipe and every message, and uses AI tools to create the two characters&apos; faces, voices and videos. The characters&apos; life story is fiction, like a family in a TV show. It&apos;s never used as proof that anything works.
      </p>
      <h2 className="mt-10 text-3xl">The guidelines every session is built on</h2>
      <ul className="mt-4 space-y-3">
        {GUIDES.map(([h, b]) => (
          <li key={h} className="card">
            <p className="text-xl font-bold">{h}</p>
            <p className="mt-1">{b}</p>
          </li>
        ))}
      </ul>
      <h2 className="mt-10 text-3xl">Our safety rules</h2>
      <ul className="mt-4 space-y-2">
        {[
          "Every movement shows a support (a counter, or a chair against the wall), an easier version, and when to stop.",
          "We never tell you to hold your breath, and we don't use loaded sit-ups or crunches.",
          "Where AI video can't show a joint position accurately, a real, credited human demonstrates it on screen.",
          "Sun Yoon grades every kitchen remedy: good evidence, some evidence, or tradition only.",
          "No cure claims, no medication advice, no diagnosis. Ever.",
          "No invented reviews or testimonials. Member quotes appear only with written permission.",
        ].map((x) => (
          <li key={x} className="flex gap-3">
            <span className="marker !bg-jade" aria-hidden="true" />
            {x}
          </li>
        ))}
      </ul>
    </div>
  );
}
