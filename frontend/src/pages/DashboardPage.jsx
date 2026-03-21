import React from "react";
import { CheckCircle2, AlertTriangle, Zap, BookOpen, Map, RotateCcw, ArrowRight } from "lucide-react";
import ResultCard from "../components/ResultCard";
import SkillTag   from "../components/SkillTag";
import ProgressBar from "../components/ProgressBar";

export default function DashboardPage({ data, role, onReset }) {
  const {
    user_skills = [], required_skills = [], skill_gap = [],
    next_skills = [], learning_path = [], match_percentage = 0,
  } = data;

  return (
    <div className="min-h-screen px-4 py-8 max-w-7xl mx-auto animate-fade-in relative z-10 w-full overflow-x-hidden">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-6 mb-10 bg-white p-6 md:p-8 rounded-3xl border border-slate-200 shadow-sm">
        <div>
          <p className="text-xs text-brand-600 font-extrabold uppercase tracking-widest mb-2 bg-brand-50 inline-block px-3 py-1 rounded-md">
            Analysis Complete
          </p>
          <h1 className="text-3xl md:text-4xl font-extrabold text-slate-900 leading-tight">
            Your Roadmap to <br className="hidden sm:block"/>
            <span className="bg-gradient-to-r from-brand-600 to-sky-500 bg-clip-text text-transparent">
              {role}
            </span>
          </h1>
        </div>
        <button
          onClick={onReset}
          className="flex items-center gap-2 text-sm font-bold text-slate-600 hover:text-slate-900
                     bg-slate-100 hover:bg-slate-200 px-5 py-3 rounded-xl
                     transition-colors shadow-sm shrink-0"
        >
          <RotateCcw className="w-4 h-4" />
          Analyze Another
        </button>
      </div>

      {/* Overview Progress */}
      <div className="bg-white p-6 md:p-8 rounded-3xl mb-8 border border-slate-200 shadow-sm animate-slide-up" style={{ animationDelay: '100ms' }}>
        <ProgressBar percent={match_percentage} />
      </div>

      {/* Grid: 3 columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6 animate-slide-up" style={{ animationDelay: '200ms' }}>
        
        <ResultCard
          title={`Your Skills (${user_skills.length})`}
          icon={<CheckCircle2 className="w-5 h-5 text-emerald-600" />}
          accent="bg-emerald-100 text-emerald-700"
        >
          {user_skills.length > 0 ? (
            <div className="flex flex-wrap gap-2.5">
              {user_skills.map((s) => <SkillTag key={s} label={s} variant="user" />)}
            </div>
          ) : (
            <EmptyState text="No skills detected in your resume." />
          )}
        </ResultCard>

        <ResultCard
          title={`Required Skills (${required_skills.length})`}
          icon={<BookOpen className="w-5 h-5 text-brand-600" />}
          accent="bg-brand-100 text-brand-700"
        >
          {required_skills.length > 0 ? (
            <div className="flex flex-wrap gap-2.5">
              {required_skills.map((s) => (
                <SkillTag key={s} label={s} variant={user_skills.includes(s) ? "user" : "required"} />
              ))}
            </div>
          ) : (
            <EmptyState text="No required skills found." />
          )}
        </ResultCard>

        <ResultCard
          title={`Skill Gap (${skill_gap.length})`}
          icon={<AlertTriangle className="w-5 h-5 text-rose-500" />}
          accent="bg-rose-100 text-rose-700"
        >
          {skill_gap.length > 0 ? (
            <div className="flex flex-wrap gap-2.5">
              {skill_gap.map((s) => <SkillTag key={s} label={s} variant="gap" />)}
            </div>
          ) : (
            <div className="flex items-center gap-2 text-emerald-600 text-sm font-bold bg-emerald-50 px-4 py-3 rounded-xl border border-emerald-100">
              <CheckCircle2 className="w-5 h-5" /> No gaps! You are role-ready 🎉
            </div>
          )}
        </ResultCard>
      </div>

      {/* Bottom section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-slide-up" style={{ animationDelay: '300ms' }}>
        
        <ResultCard
          title="Start Here – Next Skills"
          icon={<Zap className="w-5 h-5 text-orange-500" />}
          accent="bg-orange-100 text-orange-700"
        >
          {next_skills.length > 0 ? (
            <div className="flex flex-col gap-3">
              {next_skills.map((s, i) => (
                <div key={s} className="flex items-center gap-4 bg-slate-50 rounded-2xl px-5 py-3.5 border border-slate-200 hover:border-orange-200 hover:bg-orange-50 transition-colors shadow-sm group">
                  <span className="text-sm font-extrabold text-orange-500 bg-orange-100 w-7 h-7 rounded-full flex items-center justify-center shrink-0">
                    {i + 1}
                  </span>
                  <span className="text-sm text-slate-800 font-bold capitalize">{s}</span>
                  <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-orange-500 ml-auto transition-colors" />
                </div>
              ))}
            </div>
          ) : (
            <EmptyState text="No immediate recommendations — you're all set!" />
          )}
        </ResultCard>

        <ResultCard
          title={`Learning Roadmap (${learning_path.length} weeks)`}
          icon={<Map className="w-5 h-5 text-sky-500" />}
          accent="bg-sky-100 text-sky-700"
        >
          {learning_path.length > 0 ? (
            <ol className="flex flex-col gap-3 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
              {learning_path.map((entry, i) => {
                const isRevision = entry.startsWith("📚");
                return (
                  <li key={i} className={`flex items-start gap-4 rounded-2xl px-5 py-3.5 border transition-all shadow-sm
                      ${isRevision
                        ? "bg-orange-50 border-orange-200"
                        : "bg-white border-slate-200 hover:border-sky-300 hover:shadow-md"
                      }`}
                  >
                    {!isRevision && (
                      <span className="mt-0.5 text-xs font-extrabold text-white bg-sky-500 w-6 h-6 rounded-full flex items-center justify-center shrink-0 shadow-sm">
                        {i + 1}
                      </span>
                    )}
                    <span className={`text-sm font-semibold leading-relaxed ${isRevision ? "text-orange-800" : "text-slate-700"}`}>
                      {entry}
                    </span>
                  </li>
                );
              })}
            </ol>
          ) : (
            <EmptyState text="No learning path generated." />
          )}
        </ResultCard>

      </div>
    </div>
  );
}

function EmptyState({ text }) {
  return <p className="text-sm text-slate-500 font-medium italic">{text}</p>;
}
