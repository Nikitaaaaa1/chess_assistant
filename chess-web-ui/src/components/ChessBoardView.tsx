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
      try {
        newGame.load(fen);
        setGame(newGame);
      } catch (e) {
        // Partial FEN support
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
    <div className="w-full max-w-[600px] bg-slate-900 border-4 border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
        <Chessboard 
          id="BasicBoard"
          position={fen} 
          onPieceDrop={onDrop}
          boardOrientation="white"
          customDarkSquareStyle={{ backgroundColor: '#1e293b' }}
          customLightSquareStyle={{ backgroundColor: '#334155' }}
          animationDuration={200}
        />
    </div>
  );
};
