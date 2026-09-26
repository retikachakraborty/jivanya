import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/components/AuthProvider";
import { ProfileProvider } from "@/components/ProfileProvider";

export const metadata: Metadata = {
  title: "Jivanya — Food that fits your life",
  description: "Food, recipe and grocery intelligence built around the way you eat.",
  icons: {
    icon: [{ url: "/brand/jivanya-favicon.png", sizes: "512x512", type: "image/png" }],
    shortcut: "/brand/jivanya-favicon.png",
    apple: "/brand/jivanya-favicon.png",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body><AuthProvider><ProfileProvider>{children}</ProfileProvider></AuthProvider></body></html>;
}
