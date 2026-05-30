import { Chessboard } from 'react-chessboard';
import { Chess } from 'chess.js';
import { useState, useEffect } from 'react';

interface ChessBoardViewProps {
  fen: string;
  onMove?: (move: string) => void;
}

export const ChessBoardView = ({ fen, onMove }: ChessBoardViewProps) => {
  const [game, setGame] = useState(new Chess());

  useEffect(() => {
    try {
      const newGame = new Chess();
      // Try to load the FEN. If it's partial (no kings), chess.js might fail.
      // But we still want to keep the 'game' object for move validation if possible.
      try {
        newGame.load(fen);
        setGame(newGame);
      } catch (e) {
        // Partial FEN handling: if chess.js fails, we just don't update the logic object
        // but react-chessboard will still try to render the pieces from the string.
      }
    } catch (e) {
      console.error("Board Logic Error:", e);
    }
  }, [fen]);

  function onDrop(sourceSquare: string, targetSquare: string) {
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
    <div className="w-full max-w-[600px] shadow-2xl shadow-emerald-900/20 border-4 border-slate-800 rounded-lg overflow-hidden relative bg-slate-900">
      {/* Explicitly wrap in a container that ensures height for the board */}
      <div className="w-full h-full">
        <Chessboard 
          position={fen} 
          onPieceDrop={onDrop}
          boardOrientation="white"
          customDarkSquareStyle={{ backgroundColor: '#1e293b' }}
          customLightSquareStyle={{ backgroundColor: '#334155' }}
          animationDuration={200}
        />
      </div>
    </div>
  );
};
