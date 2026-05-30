import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ChessBoardView } from '../ChessBoardView'

// Mock react-chessboard
vi.mock('react-chessboard', () => ({
  Chessboard: (props: any) => <div data-testid="chessboard" data-fen={props.position} />
}))

describe('ChessBoardView', () => {
  it('renders the chessboard with provided FEN', () => {
    const fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    render(<ChessBoardView fen={fen} />)
    const board = screen.getByTestId('chessboard')
    expect(board).toBeDefined()
    expect(board.getAttribute('data-fen')).toBe(fen)
  })

  it('updates FEN when prop changes', () => {
    const startFen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    const nextFen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    
    const { rerender } = render(<ChessBoardView fen={startFen} />)
    expect(screen.getByTestId('chessboard').getAttribute('data-fen')).toBe(startFen)
    
    rerender(<ChessBoardView fen={nextFen} />)
    expect(screen.getByTestId('chessboard').getAttribute('data-fen')).toBe(nextFen)
  })
})
