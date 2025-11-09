import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TradingAgents - Alpha Arena",
  description: "AI Prediction Market Competition",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
