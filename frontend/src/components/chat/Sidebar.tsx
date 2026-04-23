import * as React from "react";
import { Clock, X } from "@phosphor-icons/react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  return (
    <>
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-[60] animate-in fade-in duration-300"
          onClick={onClose}
        />
      )}

      <aside className={cn(
        "fixed top-0 left-0 h-full w-72 bg-black/95 backdrop-blur-2xl z-[70] shadow-2xl transition-all duration-500 ease-in-out border-r border-white/5",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex flex-col h-full p-6">
          <div className="flex items-center justify-between mb-10">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-primary/20 flex items-center justify-center border border-primary/30 shadow-[0_0_15px_rgba(var(--primary-rgb),0.1)]">
                <Clock size={20} weight="bold" className="text-primary" />
              </div>
              <h2 className="text-sm font-black text-white uppercase tracking-widest">History</h2>
            </div>
            <button 
              onClick={onClose}
              className="p-2 rounded-full hover:bg-white/10 text-white/40 hover:text-white transition-all active:scale-90"
            >
              <X size={20} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 scrollbar-hide flex flex-col items-center justify-center text-center px-4">
            <div className="w-14 h-14 rounded-[22px] bg-white/5 flex items-center justify-center mb-5 border border-white/10 shadow-inner">
              <Clock size={24} weight="light" className="text-white/40" />
            </div>
            <p className="text-[11px] font-bold text-white/40 uppercase tracking-[0.2em]">No history yet</p>
          </div>

          <div className="pt-6 border-t border-white/5 mt-auto">
            <button className="w-full py-3 rounded-xl bg-primary text-white text-[12px] font-bold uppercase tracking-widest hover:scale-[1.02] active:scale-95 transition-all shadow-lg shadow-primary/20">
              New Chat
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
