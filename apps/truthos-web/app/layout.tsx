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
  title: "iN SPiRiT 生命藍圖 Life Blueprint",
  description: "iN SPiRiT 生命藍圖，由 Hermes 生命藍圖陪伴者引導的學員私密反思空間",
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
