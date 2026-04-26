import { useState, useEffect } from 'react'
import { Chessboard } from 'react-chessboard'
import { Chess } from 'chess.js'

function App() {
  const [game, setGame] = useState(new Chess())
  const [apiStatus, setApiStatus] = useState<string>('Connecting...')

  useEffect(() => {
    // Check GLAS API health
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setApiStatus(`GLAS API: ${data.status}`))
      .catch(() => setApiStatus('GLAS API: Offline'))
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8 text-center">
          Chess Assistant
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-4 rounded-xl shadow-lg">
            <Chessboard position={game.fen()} />
          </div>
          
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-md">
              <h2 className="text-xl font-semibold mb-4">Status Panel</h2>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${apiStatus.includes('healthy') ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-gray-700">{apiStatus}</span>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-xl shadow-md">
              <h2 className="text-xl font-semibold mb-4">Controls</h2>
              <button 
                onClick={() => setGame(new Chess())}
                className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
              >
                New Game
              </button>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md">
              <h2 className="text-xl font-semibold mb-4">Camera Feeds</h2>
              <div className="grid grid-cols-2 gap-2">
                <div className="aspect-video bg-gray-200 rounded flex items-center justify-center text-xs text-gray-500">Camera 1 (AVS)</div>
                <div className="aspect-video bg-gray-200 rounded flex items-center justify-center text-xs text-gray-500">Camera 2 (AVS)</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
