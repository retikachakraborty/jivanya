import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/components/AuthProvider";
import { ProfileProvider } from "@/components/ProfileProvider";

export const metadata: Metadata = {
  title: "Jivanya — Food that fits your life",
  description: "Food, recipe and grocery intelligence built around the way you eat.",
  icons: { icon: "/brand/jivanya-logo.jpeg", shortcut: "/brand/jivanya-logo.jpeg", apple: "/brand/jivanya-logo.jpeg" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body><AuthProvider><ProfileProvider>{children}</ProfileProvider></AuthProvider></body></html>;
}
