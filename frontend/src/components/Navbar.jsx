import React from "react";
import { Brain } from "lucide-react";

export default function Navbar({ currentRoute, onNavigate }) {
  const navItems = [
    { id: "home", label: "Home" },
    { id: "about", label: "About" },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/40 bg-white/70 backdrop-blur-xl supports-[backdrop-filter]:bg-white/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        
        <button 
          onClick={() => onNavigate("home")}
          className="flex items-center gap-2.5 outline-none focus:ring-2 focus:ring-brand-500 rounded-lg p-1 group"
        >
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-sky-500 shadow-[0_2px_10px_rgba(13,148,136,0.2)] flex items-center justify-center group-hover:scale-105 transition-transform">
            <Brain className="w-4 h-4 text-white" />
          </div>
          <span className="font-extrabold text-slate-800 tracking-tight text-lg">
            Skill<span className="text-brand-600">Forge</span>
          </span>
        </button>

        <div className="flex items-center gap-6">
          <nav className="hidden sm:flex items-center gap-6">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`text-sm font-bold tracking-wide transition-colors
                  ${currentRoute === item.id 
                    ? "text-brand-600" 
                    : "text-slate-500 hover:text-slate-900"
                  }`}
              >
                {item.label}
              </button>
            ))}
          </nav>
          
          {(currentRoute === "home" || currentRoute === "about") ? (
            <button 
              onClick={() => onNavigate("upload")}
              className="text-sm font-bold bg-white text-brand-700 hover:bg-brand-50 hover:text-brand-800 px-5 py-2.5 rounded-xl transition-all shadow-sm border border-slate-200"
            >
              Analyze Resume
            </button>
          ) : (
             <span className="hidden sm:inline-flex items-center gap-1.5 text-xs text-brand-700 font-bold bg-brand-50 border border-brand-200 px-3 py-1.5 rounded-full shadow-sm">
                <span className="w-2 h-2 rounded-full bg-brand-500 animate-pulse" />
                AI Active
              </span>
          )}
        </div>
      </div>
    </header>
  );
}
