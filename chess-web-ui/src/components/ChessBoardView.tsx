import { Chessboard } from 'react-chessboard';
import { Chess } from 'chess.js';
import { useState, useEffect } from 'react';

interface ChessBoardViewProps {
  fen: string;
  onMove?: (move: string) => void;
}

export const ChessBoardView = ({ fen, onMove }: ChessBoardViewProps) => {
  const [game, setGame] = useState(new Chess(fen));

  // Update local game state when external FEN prop changes
  useEffect(() => {
    try {
      // Validate FEN - if invalid (e.g. no kings), we use an empty board but 
      // safely manually set the pieces from the FEN string if possible.
      // However, react-chessboard is very resilient to FEN if we don't use the 'game' object's logic.
      
      const testGame = new Chess();
      const validation = testGame.load(fen);
      
      if (validation) {
        setGame(new Chess(fen));
      } else {
        // If FEN is technically invalid for chess.js (e.g. missing kings),
        // we still want to SHOW the pieces. 
        // We'll use a hack: set position directly to the FEN string on the component
        // but keep the internal 'game' object at its last valid state or default.
        console.warn("Rendering partial board state (invalid for logic, valid for display):", fen);
      }
    } catch (e) {
      console.error("Critical FEN error:", e);
    }
  }, [fen]);

  function onDrop(sourceSquare: string, targetSquare: string) {
    // Moves are only allowed if the board is valid
    try {
        const gameCopy = new Chess(game.fen());
        const move = gameCopy.move({
            from: sourceSquare,
            to: targetSquare,
            promotion: 'q',
        });
        if (move === null) return false;
        
        setGame(gameCopy);
        if (onMove) onMove(move.lan);
        return true;
    } catch (e) {
        return false;
    }
  }

  return (
    <div className="w-full max-w-[600px] aspect-square shadow-2xl shadow-emerald-900/20 border-4 border-slate-800 rounded-lg overflow-hidden relative">
      <Chessboard 
        position={fen} // Use external FEN directly for display (more resilient)
        onPieceDrop={onDrop}
        boardOrientation="white"
        customDarkSquareStyle={{ backgroundColor: '#1e293b' }}
        customLightSquareStyle={{ backgroundColor: '#334155' }}
      />
    </div>
  );
};
