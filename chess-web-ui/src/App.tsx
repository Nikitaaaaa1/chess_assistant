import { useState, useEffect, useRef } from 'react';
import { ChessBoardView } from './components/ChessBoardView';
import { ControlPanel } from './components/ControlPanel';
import { VisionPreview } from './components/VisionPreview';
import { Cpu, Github } from 'lucide-react';

function App() {
  const [fen, setFen] = useState("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
  const [apiStatus, setApiStatus] = useState<string>('Connecting...');
  const [isOnline, setIsOnline] = useState<boolean>(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connectWS = () => {
      const socket = new WebSocket('ws://localhost:8000/ws/game');
      
      socket.onopen = () => {
        logger.info("WebSocket connected");
        setIsOnline(true);
        setApiStatus('ALL SERVICES OPERATIONAL');
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'GAME_STATE') {
          setFen(data.fen);
        }
      };

      socket.onclose = () => {
        setIsOnline(false);
        setApiStatus('SYSTEM OFFLINE');
        // Try to reconnect after 3 seconds
        setTimeout(connectWS, 3000);
      };

      ws.current = socket;
    };

    connectWS();

    return () => {
      ws.current?.close();
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
              onMove={(move) => console.log('Board Move:', move)} 
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

// Simple logger mock since we don't have a global logger on frontend yet
const logger = {
  info: (msg: string) => console.log(`[INFO] ${msg}`),
  error: (msg: string) => console.error(`[ERROR] ${msg}`)
};

export default App
