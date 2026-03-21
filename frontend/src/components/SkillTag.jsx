import React from "react";

const VARIANTS = {
  user:     "bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100 shadow-[0_1px_2px_0_rgba(16,185,129,0.05)]",
  required: "bg-brand-50   text-brand-700   border-brand-200 hover:bg-brand-100 shadow-[0_1px_2px_0_rgba(20,184,166,0.05)]",
  gap:      "bg-rose-50    text-rose-700    border-rose-200 hover:bg-rose-100 shadow-[0_1px_2px_0_rgba(244,63,94,0.05)]",
  next:     "bg-orange-50  text-orange-700  border-orange-200 hover:bg-orange-100 shadow-[0_1px_2px_0_rgba(249,115,22,0.05)]",
};

export default function SkillTag({ label, variant = "user" }) {
  return (
    <span
      className={`
        inline-flex items-center px-3.5 py-1.5 rounded-full
        text-xs font-bold border transition-all duration-200 hover:scale-105 cursor-default
        ${VARIANTS[variant] || VARIANTS.user}
      `}
    >
      {label}
    </span>
  );
}
