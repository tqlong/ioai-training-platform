import { fireEvent, render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import { StudioHeader } from '../src/components/studio-header';

const mockPathname = vi.fn(() => '/author/problems');
vi.mock('next/navigation', () => ({
  usePathname: () => mockPathname(),
}));

describe('StudioHeader responsive navigation', () => {
  beforeEach(() => {
    mockPathname.mockReturnValue('/author/problems');
  });

  it('renders branding and primary navigation links', () => {
    render(<StudioHeader />);

    expect(screen.getByRole('link', { name: 'IOAI Studio' })).toBeTruthy();
    expect(screen.getAllByRole('link', { name: 'Problems' }).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByRole('link', { name: 'Assessment queue' }).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByRole('link', { name: 'Home' }).length).toBeGreaterThanOrEqual(1);
  });

  it('toggles mobile popup menu on hamburger button click and supports Escape key', () => {
    render(<StudioHeader />);

    const toggleButton = screen.getByRole('button', { name: 'Open navigation menu' });
    expect(toggleButton.getAttribute('aria-expanded')).toBe('false');
    expect(screen.queryByRole('menu', { name: 'Mobile navigation' })).toBeNull();

    // Open menu
    fireEvent.click(toggleButton);
    expect(screen.getByRole('button', { name: 'Close navigation menu' }).getAttribute('aria-expanded')).toBe('true');
    const menu = screen.getByRole('menu', { name: 'Mobile navigation' });
    expect(menu).toBeTruthy();

    // Close menu with Escape
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(screen.queryByRole('menu', { name: 'Mobile navigation' })).toBeNull();
    expect(screen.getByRole('button', { name: 'Open navigation menu' }).getAttribute('aria-expanded')).toBe('false');
  });

  it('closes mobile popup menu when a navigation item is clicked', () => {
    render(<StudioHeader />);

    const toggleButton = screen.getByRole('button', { name: 'Open navigation menu' });
    fireEvent.click(toggleButton);
    expect(screen.getByRole('menu', { name: 'Mobile navigation' })).toBeTruthy();

    const mobileProblemLink = screen.getByRole('menuitem', { name: 'Problems' });
    expect(mobileProblemLink).toBeTruthy();
    fireEvent.click(mobileProblemLink);

    expect(screen.queryByRole('menu', { name: 'Mobile navigation' })).toBeNull();
  });

  it('hides Problems, Assessment queue, and Home links and renders problem ID chip with copy button in preview route', () => {
    mockPathname.mockReturnValue('/author/problems/1e8cf25c-problem/preview');
    render(<StudioHeader />);

    expect(screen.getByRole('link', { name: 'IOAI Studio' })).toBeTruthy();
    expect(screen.getByText('#1e8cf25c...')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Copy problem ID' })).toBeTruthy();

    expect(screen.queryByRole('link', { name: 'Problems' })).toBeNull();
    expect(screen.queryByRole('link', { name: 'Assessment queue' })).toBeNull();
    expect(screen.queryByRole('link', { name: 'Home' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Open navigation menu' })).toBeNull();
    expect(document.getElementById('studio-header-actions')).toBeTruthy();
  });
});
