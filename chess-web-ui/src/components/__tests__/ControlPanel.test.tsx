import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ControlPanel } from '../ControlPanel';

describe('ControlPanel Component', () => {
  it('renders session control header', () => {
    render(<ControlPanel />);
    expect(screen.getByText(/Session Control/i)).toBeInTheDocument();
  });

  it('renders action buttons', () => {
    render(<ControlPanel />);
    expect(screen.getByRole('button', { name: /New Game/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Undo/i })).toBeInTheDocument();
  });

  it('displays simulation mode warning', () => {
    render(<ControlPanel />);
    expect(screen.getByText(/Simulation Active/i)).toBeInTheDocument();
  });

  it('renders difficulty slider', () => {
    render(<ControlPanel />);
    expect(screen.getByLabelText(/AI Difficulty/i)).toBeInTheDocument();
  });
});
