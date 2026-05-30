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
      // Validate FEN before setting state
      const validation = new Chess().load(fen);
      if (validation) {
        setGame(new Chess(fen));
      } else {
        console.warn("Skipping invalid FEN sync:", fen);
      }
    } catch (e) {
      console.error("Critical FEN error:", e);
    }
  }, [fen]);

  function makeAMove(move: any) {
    const gameCopy = new Chess(game.fen());
    const result = gameCopy.move(move);
    setGame(gameCopy);
    if (result && onMove) {
      onMove(result.lan);
    }
    return result;
  }

  function onDrop(sourceSquare: string, targetSquare: string) {
    const move = makeAMove({
      from: sourceSquare,
      to: targetSquare,
      promotion: 'q', // always promote to queen for simplicity in mock
    });

    if (move === null) return false;
    return true;
  }

  return (
    <div className="w-full max-w-[600px] aspect-square shadow-2xl shadow-emerald-900/20 border-4 border-slate-800 rounded-lg overflow-hidden">
      <Chessboard 
        position={game.fen()} 
        onPieceDrop={onDrop}
        boardOrientation="white"
        customDarkSquareStyle={{ backgroundColor: '#1e293b' }} // Darker slate for match
        customLightSquareStyle={{ backgroundColor: '#334155' }} // Lighter slate
      />
    </div>
  );
};
