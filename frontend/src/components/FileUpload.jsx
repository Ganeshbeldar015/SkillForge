import React, { useRef, useState } from "react";
import { Upload, FileText, X, CheckCircle } from "lucide-react";

export default function FileUpload({ onFileSelect, selectedFile }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");

  const validate = (file) => {
    setError("");
    if (!file) return;
    if (file.type !== "application/pdf") { setError("Only PDF files are supported."); return; }
    if (file.size > 10 * 1024 * 1024) { setError("File must be smaller than 10 MB."); return; }
    onFileSelect(file);
  };

  const clearFile = (e) => {
    e.stopPropagation();
    setError("");
    onFileSelect(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className="w-full">
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); validate(e.dataTransfer.files[0]); }}
        className={`
          relative cursor-pointer rounded-2xl border-2 p-8
          flex flex-col items-center justify-center gap-4 text-center
          transition-all duration-300
          ${dragging
            ? "border-brand-500 bg-brand-50 border-solid shadow-[inset_0_0_20px_rgba(20,184,166,0.1)] scale-[1.02]"
            : selectedFile
              ? "border-brand-300 bg-white border-solid shadow-[0_2px_8px_-2px_rgba(0,0,0,0.05)]"
              : "border-slate-200 border-dashed bg-white hover:border-brand-400 hover:bg-slate-50/80 shadow-[0_2px_8px_-2px_rgba(0,0,0,0.05)]"
          }
        `}
      >
        {selectedFile ? (
          <>
            <div className="w-14 h-14 rounded-full bg-brand-100 flex items-center justify-center shadow-inner mb-2">
              <CheckCircle className="w-7 h-7 text-brand-600" />
            </div>
            <div>
              <p className="font-bold text-slate-800 text-sm line-clamp-1 break-all px-8 leading-tight">{selectedFile.name}</p>
              <p className="text-xs text-brand-600 mt-1.5 font-bold tracking-wide">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <button
              onClick={clearFile}
              className="absolute top-4 right-4 p-1.5 rounded-full bg-slate-100/80 hover:bg-slate-200 text-slate-500 hover:text-slate-800 transition-colors shadow-sm"
              type="button"
            >
              <X className="w-4 h-4" />
            </button>
          </>
        ) : (
          <>
            <div className={`w-14 h-14 rounded-full flex items-center justify-center transition-all duration-300 mb-2 shadow-sm
              ${dragging ? "bg-brand-100 text-brand-600 scale-110" : "bg-slate-100 text-slate-500"}`}>
              {dragging ? <FileText className="w-6 h-6" /> : <Upload className="w-6 h-6" />}
            </div>
            <div>
              <p className="font-bold text-slate-800 text-sm tracking-wide">
                {dragging ? "Drop your resume right here" : "Click to browse or drag & drop"}
              </p>
              <p className="text-xs text-slate-500 mt-2 font-semibold">
                PDF format only · max 10 MB
              </p>
            </div>
          </>
        )}
        <input ref={inputRef} type="file" accept=".pdf" className="hidden" onChange={(e) => validate(e.target.files[0])} />
      </div>

      {error && (
        <p className="mt-3 text-xs font-bold text-red-500 flex items-center gap-1.5 justify-center bg-red-50 py-1.5 px-3 rounded-md w-max mx-auto border border-red-100">
          <X className="w-3.5 h-3.5 mb-[1px]" /> {error}
        </p>
      )}
    </div>
  );
}
