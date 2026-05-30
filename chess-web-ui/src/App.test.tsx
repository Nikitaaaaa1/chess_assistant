import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import App from './App'

// Mock react-chessboard
vi.mock('react-chessboard', () => ({
  Chessboard: () => <div data-testid="chessboard" />
}))

// Mock lucide-react
vi.mock('lucide-react', () => ({
  AlertCircle: () => <div>Alert</div>,
  Camera: () => <div>Camera</div>,
  Maximize2: () => <div>Maximize</div>,
  Cpu: () => <div>Cpu</div>,
  Github: () => <div>Github</div>
}))

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByTestId('chessboard')).toBeDefined()
  })

  it('shows connecting status initially', () => {
    render(<App />)
    expect(screen.getByText('Connecting...')).toBeDefined()
  })

  it('renders vision streams heading', () => {
    render(<App />)
    expect(screen.getByText('Vision Streams')).toBeDefined()
  })
})
