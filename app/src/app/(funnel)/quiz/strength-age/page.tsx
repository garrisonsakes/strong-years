import type { Metadata } from "next";
import { StrengthQuiz } from "@/components/quiz/StrengthQuiz";

export const metadata: Metadata = { title: "What's your Strength Age?" };

export default function Page() {
  return <StrengthQuiz />;
}
