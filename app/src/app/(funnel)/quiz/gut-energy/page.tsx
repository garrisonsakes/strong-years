import type { Metadata } from "next";
import { GutQuiz } from "@/components/quiz/GutQuiz";

export const metadata: Metadata = { title: "Sun Yoon's kitchen check" };

export default function Page() {
  return <GutQuiz />;
}
