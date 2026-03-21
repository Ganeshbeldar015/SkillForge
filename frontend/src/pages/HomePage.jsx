import React from "react";
import { Brain, Sparkles, BookOpen, Layers } from "lucide-react";

export default function HomePage({ onGetStarted }) {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-20 animate-fade-in text-center">
      <div className="flex flex-col items-center justify-center max-w-3xl mx-auto">
        
        {/* Pill badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-slate-200 shadow-sm mb-8 text-sm font-medium text-brand-600 animate-slide-up">
          <Sparkles className="w-4 h-4 text-accent-500" />
          <span>Next-Generation Career Development</span>
        </div>

        {/* Hero Heading */}
        <h1 className="text-5xl md:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.15] mb-6 animate-slide-up" style={{ animationDelay: '100ms' }}>
          Bridge the gap to your <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-sky-500">
            Dream Career
          </span>
        </h1>

        <p className="text-lg text-slate-600 mb-10 max-w-2xl leading-relaxed animate-slide-up" style={{ animationDelay: '200ms' }}>
          Upload your resume. Select your target role. Our AI instantly analyzes your skillset, 
          identifies missing competencies, and builds a customized week-by-week learning roadmap completely tailored to you.
        </p>

        <div className="flex items-center gap-4 animate-slide-up" style={{ animationDelay: '300ms' }}>
          <button onClick={onGetStarted} className="btn-primary text-lg px-8 py-4">
            Start Free Analysis
          </button>
        </div>
      </div>

      {/* Feature grid */}
      <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 text-left max-w-5xl mx-auto align-top animate-slide-up" style={{ animationDelay: '400ms' }}>
        
        <div className="glass p-8 hover:shadow-lg transition-all transform hover:-translate-y-1 duration-300">
          <div className="w-12 h-12 rounded-2xl bg-brand-100 flex items-center justify-center mb-6">
            <Brain className="w-6 h-6 text-brand-600" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-3">AI Resume Parsing</h3>
          <p className="text-slate-600 leading-relaxed">
            Our intelligent engine reads your resume like a human recruiter, precisely extracting your soft and hard skills.
          </p>
        </div>

        <div className="glass p-8 hover:shadow-lg transition-all transform hover:-translate-y-1 duration-300">
          <div className="w-12 h-12 rounded-2xl bg-sky-100 flex items-center justify-center mb-6">
            <Layers className="w-6 h-6 text-sky-600" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-3">Gap Analysis</h3>
          <p className="text-slate-600 leading-relaxed">
            We compare your extracted skills against the industry standards for your desired role, highlighting exactly what you need to learn.
          </p>
        </div>

        <div className="glass p-8 hover:shadow-lg transition-all transform hover:-translate-y-1 duration-300">
          <div className="w-12 h-12 rounded-2xl bg-accent-100 flex items-center justify-center mb-6">
            <BookOpen className="w-6 h-6 text-accent-600" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-3">Custom Roadmaps</h3>
          <p className="text-slate-600 leading-relaxed">
            Get an actionable, step-by-step curriculum with recommended topics and progression paths to make you interview-ready.
          </p>
        </div>

      </div>
    </div>
  );
}
