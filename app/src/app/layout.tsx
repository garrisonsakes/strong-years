import type { Metadata, Viewport } from "next";
import "./globals.css";
import { env } from "@/lib/config";

export const metadata: Metadata = {
  metadataBase: new URL(env.siteUrl),
  title: { default: "Strong Years: daily strength after 60", template: "%s · Strong Years" },
  description:
    "Your Daily Practice: an 8–12 minute follow-along session with Chang Yin (an AI character), Sun Yoon's recipes, and a Strength Age you retest every month.",
  robots: { index: true, follow: true },
  manifest: "/manifest.webmanifest",
  icons: { icon: "/icon-192.png", apple: "/icon-192.png" },
};

export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#1F5A46" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-btn focus:bg-ink focus:px-4 focus:py-3 focus:text-rice">
          Skip to content
        </a>
        {children}
      </body>
    </html>
  );
}
