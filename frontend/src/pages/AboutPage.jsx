import React from "react";
import { Rocket, Code2 } from "lucide-react";

export default function AboutPage({ onGetStarted }) {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 animate-fade-in">
      
      <div className="text-center mb-16">
        <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
          Empowering Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-sky-500">Learning Journey</span>
        </h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          We believe that career transitions shouldn't be a guessing game. 
          AdaptiveLearn provides clarity through intelligent data analysis.
        </p>
      </div>

      <div className="glass p-8 md:p-12 mb-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Our Mission</h2>
        <div className="prose prose-slate prose-lg text-slate-600">
          <p className="mb-4">
            The tech industry moves fast. Often, the barrier to a new role isn't a lack of motivation, 
            but a lack of direction. You don't know what you don't know. 
          </p>
          <p>
            By leveraging advanced natural language processing (NLP) and vector embeddings, 
            AdaptiveLearn reads your resume to understand your existing semantic skillset. 
            We then compare it to the most up-to-date industry requirements for your dream job to give you a definitive map forward. No more aimless tutorials—just focused growth.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
        <div className="glass p-8">
          <Rocket className="w-8 h-8 text-accent-500 mb-4" />
          <h3 className="text-xl font-bold text-slate-900 mb-2">Fast & Secure</h3>
          <p className="text-slate-600">
            Resumes are processed entirely in memory. Your personal data is never stored on our servers.
          </p>
        </div>
        <div className="glass p-8">
          <Code2 className="w-8 h-8 text-brand-500 mb-4" />
          <h3 className="text-xl font-bold text-slate-900 mb-2">Open Ecosystem</h3>
          <p className="text-slate-600">
            Built with modern web technologies: React, Tailwind, Python API, and SentenceTransformers.
          </p>
        </div>
      </div>

      <div className="text-center">
        <h3 className="text-2xl font-bold text-slate-900 mb-6">Ready to see where you stand?</h3>
        <button onClick={onGetStarted} className="btn-primary">
          Analyze My Resume
        </button>
      </div>

    </div>
  );
}
