import { useState, useEffect, useRef } from 'react';
import { ChessBoardView } from './components/ChessBoardView';
import { VisionPreview } from './components/VisionPreview';

// Simple logger mock
const logger = {
  info: (msg: string) => console.log(`%c[INFO] ${msg}`, 'color: #10b981; font-weight: bold'),
  error: (msg: string) => console.error(`%c[ERROR] ${msg}`, 'color: #ef4444; font-weight: bold'),
  debug: (msg: string) => console.debug(`%c[DEBUG] ${msg}`, 'color: #3b82f6')
};

function App() {
  const [fen, setFen] = useState("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
  const [apiStatus, setApiStatus] = useState<string>('Connecting...');
  const [isOnline, setIsOnline] = useState<boolean>(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    let reconnectTimeout: ReturnType<typeof setTimeout>;

    const connectWS = () => {
      const wsUrl = 'ws://localhost:8000/ws/game';
      logger.info(`Attempting connection to ${wsUrl}`);
      
      try {
        const socket = new WebSocket(wsUrl);
        
        socket.onopen = () => {
          logger.info("WebSocket: Connection established");
          setIsOnline(true);
          setApiStatus('ALL SERVICES OPERATIONAL');
        };

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            logger.debug(`WebSocket message received: ${data.type}`);
            if (data.type === 'GAME_STATE') {
              logger.info(`Updating board state: ${data.fen}`);
              setFen(data.fen);
            }
          } catch (err) {
            logger.error(`Failed to parse message: ${err}`);
          }
        };

        socket.onclose = (event) => {
          logger.info(`WebSocket: Connection closed (${event.code})`);
          setIsOnline(false);
          setApiStatus('SYSTEM OFFLINE');
          reconnectTimeout = setTimeout(connectWS, 3000);
        };

        socket.onerror = (err) => {
          logger.error("WebSocket: Error detected");
        };

        ws.current = socket;
      } catch (e) {
        logger.error(`WebSocket: Setup failed: ${e}`);
        reconnectTimeout = setTimeout(connectWS, 5000);
      }
    };

    connectWS();

    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (ws.current) {
        ws.current.onclose = null;
        ws.current.close();
      }
    };
  }, []);

  return (
    <div className="min-h-screen w-screen bg-slate-950 flex flex-col items-center justify-center p-4 lg:p-8">
      {/* Main Dashboard Layout - Streamlined */}
      <main className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* Left Column: Virtual Board (Span 7) */}
        <section className="lg:col-span-7 flex justify-center">
          <div className="w-full flex flex-col items-center">
            <ChessBoardView 
              fen={fen} 
              onMove={(move) => logger.info(`User attempted move: ${move}`)} 
            />
          </div>
        </section>

        {/* Right Column: Vision Preview (Span 5) */}
        <aside className="lg:col-span-5 flex flex-col gap-8 h-full justify-center">
          <VisionPreview />
          
          {/* Connection Status moved here from header/footer */}
          <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">System Connection</div>
            <div className={`text-sm font-mono ${isOnline ? 'text-emerald-500' : 'text-red-500'} flex items-center gap-2`}>
              <span className={`w-2 h-2 ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'} rounded-full`}></span>
              {apiStatus}
            </div>
          </div>
        </aside>

      </main>
    </div>
  )
}

export default App
