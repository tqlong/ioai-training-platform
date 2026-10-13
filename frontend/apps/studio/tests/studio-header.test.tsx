import { fireEvent, render, screen } from '@testing-library/react';
import { StudioHeader } from '../src/components/studio-header';

describe('StudioHeader responsive navigation', () => {
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
});
