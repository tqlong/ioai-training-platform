import type { ReactNode } from 'react';
import Link from 'next/link';
import './globals.css';

export const metadata = {
  title: 'IOAI Learn',
  description: 'Explore published IOAI training problems.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header>
          <nav aria-label="Primary">
            <Link href="/problems">IOAI Learn</Link>
            <span>•</span>
            <Link href="/">Home</Link>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
