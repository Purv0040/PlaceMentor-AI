import React from 'react';

export const Input = ({
  label,
  type = 'text',
  id,
  name,
  value,
  onChange,
  placeholder,
  error,
  icon: Icon,
  required = false,
  className = '',
  ...props
}) => {
  return (
    <div className="space-y-1.5 w-full">
      {label && (
        <label htmlFor={id || name} className="block text-xs font-medium text-slate-300">
          {label} {required && <span className="text-rose-400">*</span>}
        </label>
      )}

      <div className="relative">
        {Icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none">
            <Icon className="w-4 h-4" />
          </div>
        )}

        <input
          id={id || name}
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          className={`w-full ${
            Icon ? 'pl-9' : 'pl-3.5'
          } pr-3.5 py-2.5 rounded-xl bg-obsidian-surface border ${
            error ? 'border-rose-500/80 focus:border-rose-500' : 'border-obsidian-borderLight focus:border-brand-500'
          } text-white placeholder-slate-500 focus:outline-none text-xs transition-colors ${className}`}
          {...props}
        />
      </div>

      {error && (
        <p className="text-[11px] font-medium text-rose-400 flex items-center gap-1 mt-1">
          {error}
        </p>
      )}
    </div>
  );
};
