import type { Metadata } from "next";
import { Inter, Lora } from "next/font/google";

import { AppShell } from "@/components/app-shell";
import { AnalyticsBootstrap } from "@/src/components/analytics-bootstrap";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const lora = Lora({
  variable: "--font-lora",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TruthOS",
  description: "iN SPiRiT Life Blueprint guided reflection space",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      className={`${inter.variable} ${lora.variable} h-full antialiased`}
      lang="zh-Hant"
      suppressHydrationWarning
    >
      <body className="min-h-full bg-background text-foreground">
        <AnalyticsBootstrap />
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
