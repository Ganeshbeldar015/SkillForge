import React from "react";

export default function ProgressBar({ percent = 0 }) {
  const color =
    percent >= 75 ? "from-emerald-400 to-teal-400 shadow-[0_0_10px_rgba(52,211,153,0.3)]" :
    percent >= 40 ? "from-brand-400 to-sky-400 shadow-[0_0_10px_rgba(45,212,191,0.3)]" :
                    "from-rose-400 to-orange-400 shadow-[0_0_10px_rgba(251,113,133,0.3)]";

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-2.5">
        <span className="text-sm font-bold text-slate-700">Profile Match</span>
        <span className={`text-xl font-extrabold ${
          percent >= 75 ? "text-emerald-600" :
          percent >= 40 ? "text-brand-600"  : "text-rose-600"
        }`}>
          {percent}%
        </span>
      </div>

      <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden shadow-inner border border-slate-200/60">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${color} transition-all duration-1000 ease-out`}
          style={{ width: `${Math.min(100, Math.max(0, percent))}%` }}
        />
      </div>

      <p className="mt-2.5 text-sm font-semibold text-slate-500">
        {percent >= 75
          ? "Great match! Just a few skills to polish."
          : percent >= 40
          ? "Good foundation. Keep learning!"
          : "You're just getting started — exciting journey ahead!"}
      </p>
    </div>
  );
}
