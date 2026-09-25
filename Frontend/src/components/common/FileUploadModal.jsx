import React, { useState } from 'react';
import { X, Upload, FileText, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';

export const FileUploadModal = ({ isOpen, onClose, onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);

  if (!isOpen) return null;

  const validateFile = (selectedFile) => {
    setError('');
    if (!selectedFile) return false;
    
    // Validate file extension
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setError('Invalid format: Please upload a PDF file (.pdf).');
      return false;
    }
    
    // Validate file size (max 5MB)
    if (selectedFile.size > 5 * 1024 * 1024) {
      setError('File size too large: Maximum allowed size is 5MB.');
      return false;
    }
    
    return true;
  };

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (validateFile(selected)) {
      setFile(selected);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
      }
    }
  };

  const handleStartUpload = () => {
    if (!file) return;
    setIsUploading(true);
    setProgress(10);
    
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(interval);
          setTimeout(() => {
            setIsUploading(false);
            onUploadSuccess({
              fileName: file.name,
              fileSize: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
              pageCount: 2,
              lastAnalyzed: 'Just now'
            });
            onClose();
          }, 400);
          return 100;
        }
        return prev + 25;
      });
    }, 200);
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const mb = bytes / (1024 * 1024);
    return mb >= 1 ? `${mb.toFixed(1)} MB` : `${(bytes / 1024).toFixed(0)} KB`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-[#121624] border border-[#232b3e] rounded-2xl shadow-2xl overflow-hidden p-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#232b3e]">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
              <Upload className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-white">Upload Resume PDF</h3>
              <p className="text-xs text-slate-400">Telemetry V4.2 ATS Audit Engine</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Dropzone */}
        {!file && !isUploading && (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`mt-6 border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
              dragActive
                ? 'border-indigo-500 bg-indigo-500/10'
                : 'border-[#232b3e] hover:border-indigo-500/50 bg-[#0b0e17]'
            }`}
          >
            <input
              type="file"
              accept=".pdf"
              id="resume-dropzone-input"
              className="hidden"
              onChange={handleFileChange}
            />
            <label htmlFor="resume-dropzone-input" className="cursor-pointer flex flex-col items-center">
              <div className="w-12 h-12 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-3 shadow-inner">
                <FileText className="w-6 h-6" />
              </div>
              <p className="text-sm font-medium text-white">
                Drag and drop your resume PDF here
              </p>
              <p className="text-xs text-slate-400 mt-1">
                or <span className="text-indigo-400 hover:underline font-semibold">browse files</span> from your computer
              </p>
              <p className="text-[11px] text-slate-500 font-mono mt-4">
                Supported format: PDF only (Max 5MB)
              </p>
            </label>
          </div>
        )}

        {/* Selected File Card */}
        {file && !isUploading && (
          <div className="mt-6 p-4 rounded-xl bg-[#0b0e17] border border-[#232b3e]">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-rose-500/10 text-rose-400 flex items-center justify-center font-bold text-xs border border-rose-500/20">
                  PDF
                </div>
                <div>
                  <h4 className="text-sm font-medium text-white truncate max-w-[240px]">{file.name}</h4>
                  <p className="text-xs text-slate-400 font-mono">{formatFileSize(file.size)}</p>
                </div>
              </div>
              <button
                onClick={() => setFile(null)}
                className="text-xs text-rose-400 hover:underline px-2 py-1"
              >
                Remove
              </button>
            </div>
          </div>
        )}

        {/* Upload Progress */}
        {isUploading && (
          <div className="mt-6 p-6 rounded-xl bg-[#0b0e17] border border-indigo-500/30 text-center">
            <div className="flex items-center justify-center gap-2 text-indigo-400 text-sm font-medium mb-3">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Analyzing resume structure & keywords... ({progress}%)</span>
            </div>
            <div className="w-full bg-[#121624] rounded-full h-2 overflow-hidden border border-[#232b3e]">
              <div
                className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="mt-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-6 flex items-center justify-end gap-3 pt-4 border-t border-[#232b3e]">
          <button
            onClick={onClose}
            disabled={isUploading}
            className="px-4 py-2 rounded-xl text-sm font-medium text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleStartUpload}
            disabled={!file || isUploading}
            className="px-5 py-2 rounded-xl text-sm font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 disabled:opacity-50 flex items-center gap-2"
          >
            <Upload className="w-4 h-4" />
            <span>Run ATS Analysis</span>
          </button>
        </div>
      </div>
    </div>
  );
};
