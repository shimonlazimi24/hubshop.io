import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Frodo — Your Entire TikTok Business, One Platform",
  description:
    "Connect TikTok Shop, Ads, and Creator tools in one dashboard. Manage orders, campaigns, content, and analytics — stop switching between platforms.",
  openGraph: {
    title: "Frodo — Your Entire TikTok Business, One Platform",
    description:
      "Connect TikTok Shop, Ads, and Creator tools in one dashboard. Manage orders, campaigns, content, and analytics — stop switching between platforms.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
