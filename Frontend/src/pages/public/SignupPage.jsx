import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { User, Mail, ArrowRight, Sparkles, Github, Chrome } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Input } from '../../components/common/Input';
import { PasswordInput } from '../../components/common/PasswordInput';
import { FormError } from '../../components/common/FormError';
import { Button } from '../../components/common/Button';

export const SignupPage = () => {
  const navigate = useNavigate();
  const { signup } = useAuth();

  const [name, setName] = useState('Alex Patel');
  const [email, setEmail] = useState('alex.patel@charusat.edu.in');
  const [password, setPassword] = useState('PlacementCopilot2026!');
  const [terms, setTerms] = useState(true);
  const [formError, setFormError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const validate = () => {
    const errors = {};
    if (!name.trim()) {
      errors.name = 'Full name is required.';
    }

    if (!email) {
      errors.email = 'Email is required.';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errors.email = 'Please enter a valid college email address.';
    }

    if (!password) {
      errors.password = 'Password is required.';
    } else if (password.length < 6) {
      errors.password = 'Password must be at least 6 characters.';
    }

    if (!terms) {
      errors.terms = 'You must agree to the terms of service.';
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    if (!validate()) return;

    setIsLoading(true);
    try {
      await signup({ name, email, password });
      setIsLoading(false);
      navigate('/onboarding');
    } catch (err) {
      setIsLoading(false);
      setFormError(err.message || 'Failed to create account. Please try again.');
    }
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center p-4 sm:p-6">
      <div className="w-full max-w-md p-6 sm:p-8 rounded-2xl bg-[#121624] border border-[#232b3e] shadow-2xl space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="w-10 h-10 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400 shadow-md">
            <Sparkles className="w-5 h-5" />
          </div>
          <h2 className="text-2xl font-extrabold text-white">Create your account</h2>
          <p className="text-xs text-slate-400">Start your 90-day AI placement preparation journey</p>
        </div>

        {/* Social Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => navigate('/onboarding')}
            className="flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-[#0f131d] border border-[#232b3e] text-slate-300 hover:text-white hover:bg-[#1a2030] text-xs font-semibold transition-colors"
          >
            <Github className="w-4 h-4 text-white" /> GitHub
          </button>
          <button
            type="button"
            onClick={() => navigate('/onboarding')}
            className="flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-[#0f131d] border border-[#232b3e] text-slate-300 hover:text-white hover:bg-[#1a2030] text-xs font-semibold transition-colors"
          >
            <Chrome className="w-4 h-4 text-rose-400" /> Google
          </button>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex-1 h-[1px] bg-[#232b3e]" />
          <span className="text-[10px] uppercase font-mono text-slate-500">or sign up with email</span>
          <div className="flex-1 h-[1px] bg-[#232b3e]" />
        </div>

        <FormError message={formError} />

        {/* Signup Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Full Name"
            id="signup-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={fieldErrors.name}
            icon={User}
            placeholder="Alex Patel"
            required
          />

          <Input
            label="College Email"
            id="signup-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={fieldErrors.email}
            icon={Mail}
            placeholder="alex.patel@charusat.edu.in"
            required
          />

          <PasswordInput
            label="Password"
            id="signup-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={fieldErrors.password}
            required
          />

          <div className="space-y-1">
            <label className="flex items-start gap-2 text-xs text-slate-400 cursor-pointer select-none">
              <input
                type="checkbox"
                id="signup-terms"
                checked={terms}
                onChange={(e) => setTerms(e.target.checked)}
                className="w-4 h-4 mt-0.5 rounded border-[#232b3e] bg-[#0b0e17] text-indigo-500 focus:ring-0"
              />
              <span className="leading-snug">
                I agree to the <a href="#terms" className="text-indigo-400 hover:underline">Terms of Service</a> and <a href="#privacy" className="text-indigo-400 hover:underline">Privacy Policy</a>
              </span>
            </label>
            {fieldErrors.terms && (
              <p className="text-[11px] font-medium text-rose-400">{fieldErrors.terms}</p>
            )}
          </div>

          <Button
            type="submit"
            isLoading={isLoading}
            className="w-full"
            variant="primary"
          >
            Create Account & Start Onboarding <ArrowRight className="w-4 h-4 ml-1.5" />
          </Button>
        </form>

        {/* Footer Link */}
        <div className="text-center text-xs text-slate-400">
          Already have an account?{' '}
          <NavLink to="/login" className="text-indigo-400 font-bold hover:underline">
            Log in
          </NavLink>
        </div>
      </div>
    </div>
  );
};
