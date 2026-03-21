import React from "react";
import { ChevronDown, Briefcase } from "lucide-react";

const FALLBACK_ROLES = [
  "AI Engineer", "Web Developer", "Data Scientist", "Data Analyst",
  "Backend Developer", "Frontend Developer", "DevOps Engineer", "NLP Engineer"
];

export default function RoleSelector({ value, onChange, roles = [] }) {
  const options = roles.length > 0 ? roles : FALLBACK_ROLES;

  return (
    <div className="w-full relative">
      <label className="block text-sm font-bold text-slate-800 mb-2">
        Target Role
      </label>

      <div className="relative">
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 z-10">
          <Briefcase className="w-4 h-4 text-brand-500" />
        </div>

        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="
            w-full appearance-none pl-11 pr-10 py-3.5
            bg-white border-[1.5px] border-slate-200 hover:border-brand-300 rounded-xl
            text-slate-900 text-sm font-bold shadow-[0_2px_8px_-2px_rgba(0,0,0,0.05)]
            focus:outline-none focus:ring-[3px] focus:ring-brand-500/20 focus:border-brand-500
            transition-all duration-200 cursor-pointer
          "
        >
          <option value="" disabled className="text-slate-500 font-semibold">
            Select your dream job…
          </option>
          {options.map((role) => (
            <option key={role} value={role} className="font-bold text-slate-800 bg-white shadow-none">
              {role}
            </option>
          ))}
        </select>

        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
          <ChevronDown className="w-5 h-5 text-slate-400" />
        </div>
      </div>
    </div>
  );
}
