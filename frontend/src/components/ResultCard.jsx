import React from "react";

export default function ResultCard({ title, icon, accent = "bg-brand-100 text-brand-600", children, className = "" }) {
  return (
    <div
      className={`
        bg-white border border-slate-200 rounded-3xl p-6 flex flex-col gap-5 shadow-sm hover:shadow-md transition-shadow duration-300
        ${className}
      `}
    >
      <div className="flex items-center gap-3.5">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-inner ${accent}`}>
          {icon}
        </div>
        <h3 className="text-base font-extrabold text-slate-800 tracking-wide">{title}</h3>
      </div>
      <div>{children}</div>
    </div>
  );
}
