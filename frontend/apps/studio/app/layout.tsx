import type { ReactNode } from 'react';
import Link from 'next/link';
import './globals.css';

export const metadata = {
  title: 'IOAI Studio',
  description: 'Authoring and publication workspace for IOAI Release 0.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header>
          <nav aria-label="Primary">
            <Link href="/author/problems">IOAI Studio</Link>
            <span>•</span>
            <Link href="/">Home</Link>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
