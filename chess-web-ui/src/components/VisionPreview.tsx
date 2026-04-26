import { Camera, Maximize2 } from 'lucide-react';

export const VisionPreview = () => {
  return (
    <div className="flex flex-col gap-4 bg-slate-900/50 p-6 rounded-xl border border-slate-800 backdrop-blur-sm h-full">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-2">
        <h2 className="text-xl font-bold flex items-center gap-2 text-blue-400">
          <Camera size={20} />
          Vision Streams
        </h2>
      </div>

      <div className="flex flex-col gap-4 flex-1">
        {/* Camera A */}
        <div className="relative group flex-1 bg-slate-950 rounded-lg border border-slate-800 overflow-hidden min-h-[160px]">
          <div className="absolute top-2 left-2 px-2 py-0.5 bg-black/60 rounded text-[10px] font-bold text-slate-300 uppercase z-10">
            CAM A: Board Warped
          </div>
          <div className="w-full h-full flex items-center justify-center text-slate-700 italic text-xs">
            No stream signal...
          </div>
          <button className="absolute bottom-2 right-2 p-1.5 bg-black/40 hover:bg-black/80 rounded transition-colors opacity-0 group-hover:opacity-100">
            <Maximize2 size={14} className="text-slate-400" />
          </button>
        </div>

        {/* Camera B */}
        <div className="relative group flex-1 bg-slate-950 rounded-lg border border-slate-800 overflow-hidden min-h-[160px]">
          <div className="absolute top-2 left-2 px-2 py-0.5 bg-black/60 rounded text-[10px] font-bold text-slate-300 uppercase z-10">
            CAM B: Board Warped
          </div>
          <div className="w-full h-full flex items-center justify-center text-slate-700 italic text-xs">
            No stream signal...
          </div>
          <button className="absolute bottom-2 right-2 p-1.5 bg-black/40 hover:bg-black/80 rounded transition-colors opacity-0 group-hover:opacity-100">
            <Maximize2 size={14} className="text-slate-400" />
          </button>
        </div>
      </div>
      
      <div className="mt-2 text-center">
        <p className="text-[10px] font-mono text-slate-500">
          DATA FUSION ACCURACY: <span className="text-emerald-500">N/A</span>
        </p>
      </div>
    </div>
  );
};
