import React, { useEffect, useState } from "react";
import { Sparkles, ArrowRight, AlertCircle, Loader2 } from "lucide-react";
import FileUpload from "../components/FileUpload";
import RoleSelector from "../components/RoleSelector";
import { analyzeResume, fetchRoles } from "../services/api";

export default function UploadPage({ onSuccess }) {
  const [file, setFile]       = useState(null);
  const [role, setRole]       = useState("");
  const [roles, setRoles]     = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  useEffect(() => {
    fetchRoles()
      .then(setRoles)
      .catch(() => console.warn("Using fallback roles."));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!file) { setError("Please upload your PDF resume first."); return; }
    if (!role) { setError("Please select a target role."); return; }

    setLoading(true);
    try {
      const data = await analyzeResume(file, role);
      onSuccess(data, role);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full flex flex-col items-center justify-center px-4 max-w-7xl mx-auto h-full animate-fade-in relative z-10">
      
      <div className="text-center mb-10 w-full mt-4">
        <div className="inline-flex items-center gap-2 bg-accent-50 text-accent-700 border border-accent-200 rounded-full px-4 py-1.5 text-xs font-bold uppercase tracking-widest mb-6 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-accent-500" />
          Intelligent Gap Analysis
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight max-w-3xl mx-auto">
          Map your journey to <br className="hidden sm:block"/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-sky-500">Skill Mastery</span>
        </h1>
      </div>

      <form onSubmit={handleSubmit} className="w-full max-w-[500px] glass p-8 sm:p-10 flex flex-col gap-6 relative">
        {loading && (
          <div className="absolute inset-0 bg-white/70 backdrop-blur-md z-10 rounded-3xl flex flex-col items-center justify-center">
            <Loader2 className="w-10 h-10 text-brand-600 animate-spin mb-4" />
            <p className="text-slate-900 font-extrabold text-lg animate-pulse">Running semantic analysis...</p>
            <p className="text-slate-600 font-medium text-sm mt-1">Extracting skills from document</p>
          </div>
        )}
        
        <div>
          <label className="block text-sm font-bold text-slate-800 mb-2">
            Your Resume (PDF)
          </label>
          <FileUpload onFileSelect={setFile} selectedFile={file} />
        </div>

        <RoleSelector value={role} onChange={setRole} roles={roles} />

        {error && (
          <div className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl px-4 py-3 shadow-sm">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 shrink-0" />
            <p className="text-sm font-bold text-red-800">{error}</p>
          </div>
        )}

        <button type="submit" disabled={loading} className="btn-primary mt-2 flex items-center justify-center gap-2 w-full text-lg shadow-[0_4px_14px_0_rgba(13,148,136,0.39)]">
           Generate Career Roadmap
           <ArrowRight className="w-5 h-5" />
        </button>
        
        <p className="text-center text-xs text-slate-500 font-semibold mt-1">
          Your file is processed locally and discarded immediately.
        </p>
      </form>
    </div>
  );
}
