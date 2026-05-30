import { Play, RotateCcw, Settings2, ShieldAlert } from 'lucide-react';

export const ControlPanel = () => {
  return (
    <div className="flex flex-col gap-4 bg-slate-900/50 p-6 rounded-xl border border-slate-800 backdrop-blur-sm">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-2">
        <h2 className="text-xl font-bold flex items-center gap-2 text-emerald-400">
          <Settings2 size={20} />
          Session Control
        </h2>
        <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-mono rounded border border-emerald-500/20">
          READY
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <button 
          onClick={() => console.log('Mock: New Game')}
          className="flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 transition-colors py-2.5 px-4 rounded-lg font-semibold text-sm"
        >
          <Play size={16} fill="currentColor" />
          New Game
        </button>
        <button 
          onClick={() => console.log('Mock: Undo Move')}
          className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 transition-colors py-2.5 px-4 rounded-lg font-semibold text-sm border border-slate-700"
        >
          <RotateCcw size={16} />
          Undo
        </button>
      </div>

      <div className="mt-4">
        <label 
          htmlFor="ai-difficulty"
          className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block"
        >
          AI Difficulty (Stockfish)
        </label>
        <input 
          id="ai-difficulty"
          type="range" 
          min="1" 
          max="20" 
          defaultValue="10"
          className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500" 
        />
        <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
          <span>Level 1</span>
          <span>Level 20</span>
        </div>
      </div>

      <div className="mt-4 p-3 bg-amber-500/5 border border-amber-500/20 rounded-lg flex gap-3 items-start">
        <ShieldAlert className="text-amber-500 shrink-0 mt-0.5" size={16} />
        <div>
          <p className="text-xs font-bold text-amber-500 mb-0.5 uppercase">Simulation Active</p>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            No physical board connected. Moves made on the virtual board are processed locally.
          </p>
        </div>
      </div>
    </div>
  );
};
