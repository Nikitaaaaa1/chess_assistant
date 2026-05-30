import { useState, useEffect, useRef } from 'react';
import { ChessBoardView } from './components/ChessBoardView';
import { VisionPreview } from './components/VisionPreview';
import { AlertCircle } from 'lucide-react';

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
  const [isValid, setIsValid] = useState<boolean>(true);
  const [validationMsg, setValidationMsg] = useState<string>('');
  
  const ws = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const connectWS = () => {
      // Avoid multiple connections
      if (ws.current && (ws.current.readyState === WebSocket.OPEN || ws.current.readyState === WebSocket.CONNECTING)) {
        return;
      }

      const wsUrl = 'ws://localhost:8000/ws/game';
      logger.info(`WebSocket: Connecting to ${wsUrl}`);
      
      const socket = new WebSocket(wsUrl);
      
      socket.onopen = () => {
        logger.info("WebSocket: Connection established");
        setIsOnline(true);
        setApiStatus('ALL SERVICES OPERATIONAL');
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'GAME_STATE') {
            logger.debug(`[SYNC] New FEN received: ${data.fen}`);
            setFen(data.fen);
            setIsValid(data.is_valid);
            setValidationMsg(data.validation_msg);
          }
        } catch (err) {
          logger.error(`WebSocket: Message parse error: ${err}`);
        }
      };

      socket.onclose = (event) => {
        logger.info(`WebSocket: Connection closed (${event.code})`);
        setIsOnline(false);
        setApiStatus('SYSTEM OFFLINE');
        if (reconnectRef.current) clearTimeout(reconnectRef.current);
        reconnectRef.current = setTimeout(connectWS, 3000);
      };

      socket.onerror = () => {
        logger.error("WebSocket: Error occurred");
      };

      ws.current = socket;
    };

    connectWS();

    return () => {
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      if (ws.current) {
        ws.current.onclose = null; // Prevent reconnect on cleanup
        ws.current.close();
      }
    };
  }, []);

  return (
    <div className="min-h-screen w-screen bg-slate-950 flex items-center justify-center p-4">
      <main className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        
        {/* Left Column: Virtual Board (Span 7) */}
        <section className="lg:col-span-7 flex flex-col items-center">
          <div className="w-full flex justify-center relative">
            {/* FORCE RE-RENDER on FEN change using key */}
            <ChessBoardView 
              key={fen}
              fen={fen} 
              onMove={(move) => logger.info(`User move: ${move}`)} 
            />
            
            {!isValid && (
                <div className="absolute top-4 right-4 z-50">
                    <div className="bg-amber-500/90 text-slate-950 px-3 py-1.5 rounded-lg font-bold flex items-center gap-2 text-[10px] uppercase tracking-tighter shadow-2xl backdrop-blur-md border border-amber-400">
                        <AlertCircle size={14} />
                        {validationMsg}
                    </div>
                </div>
            )}
          </div>
        </section>

        {/* Right Column: Vision Preview (Span 5) */}
        <aside className="lg:col-span-5 flex flex-col gap-6">
          <VisionPreview />
          
          <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 flex items-center justify-between shadow-lg">
            <div className="flex flex-col">
                <span className="text-[9px] text-slate-500 font-black uppercase tracking-[0.2em] mb-1">Network Status</span>
                <span className={`text-xs font-mono ${isOnline ? 'text-emerald-400' : 'text-red-400'} flex items-center gap-2`}>
                <span className={`w-2 h-2 ${isOnline ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'} rounded-full`}></span>
                {apiStatus}
                </span>
            </div>
            <div className="hidden lg:block text-[8px] font-mono text-slate-600 max-w-[240px] truncate bg-black/20 p-2 rounded">
                CURRENT FEN: {fen}
            </div>
          </div>
        </aside>

      </main>
    </div>
  )
}

export default App
