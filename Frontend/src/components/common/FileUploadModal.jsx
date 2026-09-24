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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-obsidian-950/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-surface-container-high border border-outline-variant rounded-2xl shadow-2xl overflow-hidden p-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-outline-variant/50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-primary-container/20 text-primary border border-primary/30">
              <Upload className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-on-surface">Upload Resume PDF</h3>
              <p className="text-xs text-on-surface-variant">Telemetry V4.2 ATS Audit Engine</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors"
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
                ? 'border-primary bg-primary-container/10'
                : 'border-outline-variant hover:border-primary/50 bg-surface-container-low/50'
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
              <div className="w-12 h-12 rounded-full bg-surface-container flex items-center justify-center text-primary mb-3 shadow-inner">
                <FileText className="w-6 h-6" />
              </div>
              <p className="text-sm font-medium text-on-surface">
                Drag and drop your resume PDF here
              </p>
              <p className="text-xs text-on-surface-variant mt-1">
                or <span className="text-primary hover:underline font-semibold">browse files</span> from your computer
              </p>
              <p className="text-[11px] text-outline font-mono mt-4">
                Supported format: PDF only (Max 5MB)
              </p>
            </label>
          </div>
        )}

        {/* Selected File Card */}
        {file && !isUploading && (
          <div className="mt-6 p-4 rounded-xl bg-surface-container-low border border-outline-variant">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-error/10 text-error flex items-center justify-center font-bold text-xs border border-error/20">
                  PDF
                </div>
                <div>
                  <h4 className="text-sm font-medium text-on-surface truncate max-w-[240px]">{file.name}</h4>
                  <p className="text-xs text-on-surface-variant font-mono">{formatFileSize(file.size)}</p>
                </div>
              </div>
              <button
                onClick={() => setFile(null)}
                className="text-xs text-error hover:underline px-2 py-1"
              >
                Remove
              </button>
            </div>
          </div>
        )}

        {/* Upload Progress */}
        {isUploading && (
          <div className="mt-6 p-6 rounded-xl bg-surface-container-low border border-primary/30 text-center">
            <div className="flex items-center justify-center gap-2 text-primary text-sm font-medium mb-3">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Analyzing resume structure & keywords... ({progress}%)</span>
            </div>
            <div className="w-full bg-surface-container rounded-full h-2 overflow-hidden border border-outline-variant">
              <div
                className="bg-primary h-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="mt-4 p-3 rounded-lg bg-error/10 border border-error/30 text-error text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-6 flex items-center justify-end gap-3 pt-4 border-t border-outline-variant/50">
          <button
            onClick={onClose}
            disabled={isUploading}
            className="px-4 py-2 rounded-xl text-sm font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleStartUpload}
            disabled={!file || isUploading}
            className="px-5 py-2 rounded-xl text-sm font-semibold bg-primary text-on-primary hover:bg-primary-fixed-dim transition-all shadow-md disabled:opacity-50 flex items-center gap-2"
          >
            <Upload className="w-4 h-4" />
            <span>Run ATS Analysis</span>
          </button>
        </div>
      </div>
    </div>
  );
};
