import type { ReactNode } from 'react';
import './globals.css';
import { StudioHeader } from '../src/components/studio-header';

export const metadata = {
  title: 'IOAI Studio',
  description: 'Authoring and publication workspace for IOAI Release 0.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <StudioHeader />
        <main>{children}</main>
      </body>
    </html>
  );
}
