import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Alpha Arena - AI Prediction Market Competition",
  description: "5 Leading AI Models Compete on Opinion.trade (BNB Chain) - Autonomous Prediction Market Competition",
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
