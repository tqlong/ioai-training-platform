'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Check, Copy } from 'lucide-react';

export function StudioHeader() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const toggleRef = useRef<HTMLButtonElement>(null);

  const isPreviewPage = Boolean(pathname && pathname.endsWith('/preview'));
  const previewProblemId = isPreviewPage ? pathname?.split('/')[3] : null;

  const isEditorPage = Boolean(
    pathname &&
    pathname.startsWith('/author/problems/') &&
    pathname !== '/author/problems/new' &&
    !isPreviewPage,
  );

  useEffect(() => {
    if (!isOpen || isEditorPage || isPreviewPage) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
        toggleRef.current?.focus();
      }
    };

    const handleClickOutside = (event: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node) &&
        toggleRef.current &&
        !toggleRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, isEditorPage, isPreviewPage]);

  const handleCopy = (key: string, text: string) => {
    void navigator.clipboard?.writeText?.(text);
    setCopiedKey(key);
    window.setTimeout(() => setCopiedKey((curr) => (curr === key ? null : curr)), 1500);
  };

  const closeMenu = () => setIsOpen(false);

  if (isEditorPage) return null;

  return (
    <header className="studio-header">
      <nav aria-label="Primary" className="studio-nav">
        <div className="studio-brand-container">
          {isPreviewPage && previewProblemId ? (
            <div className="editor-brand-group">
              <Link href="/author/problems" className="studio-brand" onClick={closeMenu}>
                <span className="studio-brand-title">IOAI Studio</span>
              </Link>
              <span className="editor-nav-sep" aria-hidden="true">/</span>
              <span className="problem-id-chip dark-chip">
                #{previewProblemId.length > 8 ? `${previewProblemId.slice(0, 8)}...` : previewProblemId}
                <button
                  type="button"
                  className="copy-chip-btn dark-copy"
                  onClick={() => handleCopy('header-problem-id', previewProblemId)}
                  title={copiedKey === 'header-problem-id' ? 'Copied!' : `Copy full ID: ${previewProblemId}`}
                  aria-label="Copy problem ID"
                >
                  {copiedKey === 'header-problem-id' ? (
                    <Check className="copy-check-icon" size={13} aria-hidden="true" />
                  ) : (
                    <Copy size={13} aria-hidden="true" />
                  )}
                </button>
              </span>
            </div>
          ) : (
            <Link href="/author/problems" className="studio-brand" onClick={closeMenu}>
              <span className="studio-brand-title">IOAI Studio</span>
            </Link>
          )}
        </div>

        {/* In preview page, remove navigation links and show the slot for preview actions */}
        {isPreviewPage ? (
          <div id="studio-header-actions" className="studio-header-actions" />
        ) : (
          <>
            {/* Desktop navigation links */}
            <div className="studio-nav-links">
              <Link href="/author/problems" className="studio-nav-link">Problems</Link>
              <span className="studio-nav-divider" aria-hidden="true">•</span>
              <Link href="/author/assessments" className="studio-nav-link">Assessment queue</Link>
              <span className="studio-nav-divider" aria-hidden="true">•</span>
              <Link href="/" className="studio-nav-link">Home</Link>
            </div>

            {/* Mobile hamburger toggle button */}
            <button
              ref={toggleRef}
              aria-controls="studio-mobile-menu"
              aria-expanded={isOpen}
              aria-label={isOpen ? 'Close navigation menu' : 'Open navigation menu'}
              className="studio-menu-toggle"
              onClick={() => setIsOpen((prev) => !prev)}
              type="button"
            >
              <span className="studio-hamburger-icon" aria-hidden="true">
                <span className={`hamburger-bar ${isOpen ? 'bar-top-open' : ''}`} />
                <span className={`hamburger-bar ${isOpen ? 'bar-mid-open' : ''}`} />
                <span className={`hamburger-bar ${isOpen ? 'bar-bot-open' : ''}`} />
              </span>
            </button>

            {/* Mobile popup menu */}
            {isOpen && (
              <div
                id="studio-mobile-menu"
                ref={menuRef}
                className="studio-mobile-popup"
                role="menu"
                aria-label="Mobile navigation"
              >
                <div className="studio-mobile-popup-inner">
                  <Link
                    href="/author/problems"
                    className="studio-mobile-nav-link"
                    onClick={closeMenu}
                    role="menuitem"
                  >
                    Problems
                  </Link>
                  <Link
                    href="/author/assessments"
                    className="studio-mobile-nav-link"
                    onClick={closeMenu}
                    role="menuitem"
                  >
                    Assessment queue
                  </Link>
                  <Link
                    href="/"
                    className="studio-mobile-nav-link"
                    onClick={closeMenu}
                    role="menuitem"
                  >
                    Home
                  </Link>
                </div>
              </div>
            )}
          </>
        )}
      </nav>
    </header>
  );
}
