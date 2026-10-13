'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';

export function StudioHeader() {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const toggleRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!isOpen) return;

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
  }, [isOpen]);

  const closeMenu = () => setIsOpen(false);

  return (
    <header className="studio-header">
      <nav aria-label="Primary" className="studio-nav">
        <div className="studio-brand-container">
          <Link href="/author/problems" className="studio-brand" onClick={closeMenu}>
            <span className="studio-brand-title">IOAI Studio</span>
          </Link>
        </div>

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
                role="menuitem"
                onClick={closeMenu}
              >
                Problems
              </Link>
              <Link
                href="/author/assessments"
                className="studio-mobile-nav-link"
                role="menuitem"
                onClick={closeMenu}
              >
                Assessment queue
              </Link>
              <Link
                href="/"
                className="studio-mobile-nav-link"
                role="menuitem"
                onClick={closeMenu}
              >
                Home
              </Link>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
