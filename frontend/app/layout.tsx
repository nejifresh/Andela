import type { Metadata } from "next";
import Link from "next/link";
import { Activity, ClipboardList, ShieldCheck } from "lucide-react";
import "./globals.css";

export const metadata: Metadata = {
  title: "CloudWaste Sentinel",
  description: "Evidence-backed cloud cost remediation dashboard"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-line bg-white">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
              <Link href="/" className="flex items-center gap-3">
                <span className="flex h-9 w-9 items-center justify-center rounded-md bg-ink text-white">
                  <ShieldCheck size={20} />
                </span>
                <span>
                  <span className="block text-lg font-semibold text-ink">CloudWaste Sentinel</span>
                  <span className="block text-xs text-steel">FinOps remediation, generated only</span>
                </span>
              </Link>
              <nav className="flex items-center gap-2 text-sm">
                <Link className="flex items-center gap-2 rounded-md px-3 py-2 text-steel hover:bg-panel hover:text-ink" href="/">
                  <Activity size={16} /> Dashboard
                </Link>
                <Link className="flex items-center gap-2 rounded-md px-3 py-2 text-steel hover:bg-panel hover:text-ink" href="/audit">
                  <ClipboardList size={16} /> Audit
                </Link>
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-7xl px-6 py-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
