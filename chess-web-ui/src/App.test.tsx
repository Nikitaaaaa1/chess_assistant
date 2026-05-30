import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import App from './App'

// Mock react-chessboard since it might have issues in jsdom
vi.mock('react-chessboard', () => ({
  Chessboard: () => <div data-testid="chessboard" />
}))

describe('App', () => {
  it('renders the title', () => {
    render(<App />)
    expect(screen.getByText('Chess Assistant')).toBeDefined()
  })

  it('shows connecting status initially', () => {
    render(<App />)
    expect(screen.getByText('Connecting...')).toBeDefined()
  })
})
