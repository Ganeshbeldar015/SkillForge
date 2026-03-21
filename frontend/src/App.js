import React, { useState } from "react";
import Navbar        from "./components/Navbar";
import HomePage      from "./pages/HomePage";
import UploadPage    from "./pages/UploadPage";
import DashboardPage from "./pages/DashboardPage";
import AboutPage     from "./pages/AboutPage";
import RainbowCursor from "./components/RainbowCursor";

/**
 * App.js – Root component
 * -----------------------
 * State-based multi-page routing.
 */
export default function App() {
  const [page, setPage]     = useState("home");   // "home" | "upload" | "dashboard" | "about"
  const [result, setResult] = useState(null);      // API response data
  const [role, setRole]     = useState("");        // selected target role

  const handleSuccess = (data, selectedRole) => {
    setResult(data);
    setRole(selectedRole);
    setPage("dashboard");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleReset = () => {
    setResult(null);
    setRole("");
    setPage("upload");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 selection:bg-brand-200 selection:text-brand-900 flex flex-col relative overflow-hidden">
      
      <RainbowCursor />
      {/* Abstract light mode background elements */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-brand-200/40 rounded-full blur-[100px]" />
        <div className="absolute bottom-[-10%] right-[-5%] w-[600px] h-[600px] bg-sky-200/40 rounded-full blur-[120px]" />
        <div className="absolute top-[20%] right-[10%] w-[300px] h-[300px] bg-accent-200/30 rounded-full blur-[80px]" />
        {/* Subtle grid pattern */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.015] mix-blend-multiply"></div>
      </div>

      <Navbar currentRoute={page} onNavigate={setPage} />

      <main className="flex-1 pt-20 pb-12 z-10 w-full relative">
        {page === "home" && (
          <HomePage onGetStarted={() => setPage("upload")} />
        )}
        
        {page === "upload" && (
          <UploadPage onSuccess={handleSuccess} />
        )}

        {page === "dashboard" && result && (
          <DashboardPage data={result} role={role} onReset={handleReset} />
        )}

        {/* Fallback to upload if dashboard is clicked without results */}
        {page === "dashboard" && !result && (
          <UploadPage onSuccess={handleSuccess} />
        )}

        {page === "about" && (
          <AboutPage onGetStarted={() => setPage("upload")} />
        )}
      </main>
    </div>
  );
}
