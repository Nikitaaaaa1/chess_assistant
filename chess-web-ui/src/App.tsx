import { useState, useEffect, useRef } from 'react';
import { ChessBoardView } from './components/ChessBoardView';
import { ControlPanel } from './components/ControlPanel';
import { VisionPreview } from './components/VisionPreview';
import { Cpu, Github } from 'lucide-react';

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
    <div className="min-h-screen w-screen bg-slate-950 flex flex-col items-center p-4 lg:p-8">
      {/* Header */}
      <header className="w-full max-w-7xl flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-black tracking-tighter text-white flex items-center gap-3">
            <Cpu className="text-emerald-500" size={32} />
            CHESS <span className="text-emerald-500 underline decoration-4 underline-offset-4">ASSISTANT</span>
          </h1>
          <p className="text-slate-500 text-sm font-medium mt-1 uppercase tracking-widest">
            Real-Time Computer Vision Tracking System
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <a href="#" className="p-2 bg-slate-900 rounded-full border border-slate-800 hover:text-emerald-400 transition-colors">
            <Github size={20} />
          </a>
          <div className="text-right hidden md:block">
            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">System Status</div>
            <div className={`text-sm font-mono ${isOnline ? 'text-emerald-500' : 'text-red-500'} flex items-center justify-end gap-2`}>
              <span className={`w-2 h-2 ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'} rounded-full`}></span>
              {apiStatus}
            </div>
          </div>
        </div>
      </header>

      {/* Main Dashboard Layout */}
      <main className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Virtual Board (Span 7) */}
        <section className="lg:col-span-7 flex justify-center">
          <div className="w-full flex flex-col items-center">
            <ChessBoardView 
              fen={fen} 
              onMove={(move) => logger.info(`User attempted move: ${move}`)} 
            />
            <div className="mt-6 w-full flex justify-between px-2 text-[10px] font-mono text-slate-500 uppercase tracking-widest">
              <span>View: Standard (White)</span>
              <span>Coordinates: Enabled</span>
            </div>
          </div>
        </section>

        {/* Right Column: Controls & Vision (Span 5) */}
        <aside className="lg:col-span-5 flex flex-col gap-8 h-full">
          <ControlPanel />
          <VisionPreview />
        </aside>

      </main>

      {/* Footer / Logs */}
      <footer className="w-full max-w-7xl mt-12 pt-6 border-t border-slate-900 flex justify-between text-[10px] font-mono text-slate-600">
        <p>© 2026 UNIVERSITY AI CHESS PROJECT</p>
        <div className="flex gap-6">
          <span className="flex gap-2 underline decoration-emerald-900">v0.1.0-alpha</span>
          <span className="flex gap-2 underline decoration-emerald-900 italic">Stage: Frontend Prototype</span>
        </div>
      </footer>
    </div>
  )
}

export default App
