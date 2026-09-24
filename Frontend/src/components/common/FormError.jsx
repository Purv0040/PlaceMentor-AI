import React from 'react';
import { AlertCircle } from 'lucide-react';

export const FormError = ({ message }) => {
  if (!message) return null;

  return (
    <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-medium flex items-start gap-2.5">
      <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
      <span className="leading-snug">{message}</span>
    </div>
  );
};
