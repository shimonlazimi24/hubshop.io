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
  title: "Frodo — One Platform to Rule Them All",
  description:
    "Frodo unifies TikTok Shop, Ads, and Creator tools into one platform. Manage orders, campaigns, content, and analytics — one platform to rule them all.",
  openGraph: {
    title: "Frodo — One Platform to Rule Them All",
    description:
      "Frodo unifies TikTok Shop, Ads, and Creator tools into one platform. Manage orders, campaigns, content, and analytics — one platform to rule them all.",
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
