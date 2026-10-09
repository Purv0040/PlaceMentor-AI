import React, { useState, useEffect, useCallback } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { User, Mail, ArrowRight, Sparkles, Github, Chrome, Loader2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useUser } from '../../context/UserContext';
import { useOnboarding } from '../../context/OnboardingContext';
import { Input } from '../../components/common/Input';
import { PasswordInput } from '../../components/common/PasswordInput';
import { FormError } from '../../components/common/FormError';
import { Button } from '../../components/common/Button';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

export const SignupPage = () => {
  const navigate = useNavigate();
  const { signup, googleLogin } = useAuth();
  const { updateUserProfile } = useUser();
  const { updateProfile } = useOnboarding();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [terms, setTerms] = useState(false);
  const [formError, setFormError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  const handleGoogleResponse = useCallback(async (response) => {
    if (!response?.credential) {
      setFormError('Google sign-up failed. Please try again.');
      return;
    }

    setIsGoogleLoading(true);
    setFormError('');
    try {
      const res = await googleLogin(response.credential);
      const currentUser = res.user;
      updateUserProfile(currentUser);
      updateProfile({ name: currentUser.name || currentUser.full_name, email: currentUser.email });

      const isOnboarded = currentUser?.is_onboarded === true ||
        (currentUser?.is_onboarded !== false &&
          localStorage.getItem('placementCopilotOnboardingComplete') === 'true');

      if (isOnboarded) {
        navigate('/dashboard', { replace: true });
      } else {
        navigate('/onboarding/profile', { replace: true });
      }
    } catch (err) {
      setFormError(err.message || 'Google sign-up failed. Please try again.');
    } finally {
      setIsGoogleLoading(false);
    }
  }, [googleLogin, updateUserProfile, updateProfile, navigate]);

  useEffect(() => {
    if (!GOOGLE_CLIENT_ID || !window.google?.accounts?.id) return;

    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback: handleGoogleResponse,
      auto_select: false,
      cancel_on_tap_outside: true,
    });
  }, [handleGoogleResponse]);

  const handleGoogleClick = () => {
    if (!GOOGLE_CLIENT_ID) {
      setFormError('Google Sign-In is not configured.');
      return;
    }
    if (!window.google?.accounts?.id) {
      setFormError('Google Sign-In is loading. Please wait a moment and try again.');
      return;
    }
    setFormError('');
    window.google.accounts.id.prompt((notification) => {
      if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
        const tempDiv = document.createElement('div');
        tempDiv.style.display = 'none';
        document.body.appendChild(tempDiv);
        window.google.accounts.id.renderButton(tempDiv, {
          type: 'standard',
          size: 'large',
        });
        const btn = tempDiv.querySelector('[role="button"]') || tempDiv.querySelector('div[tabindex]');
        if (btn) btn.click();
        setTimeout(() => document.body.removeChild(tempDiv), 100);
      }
    });
  };

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
      const res = await signup({ name, email, password });
      updateUserProfile({ name, email });
      updateProfile({ name, email });
      setIsLoading(false);
      navigate('/onboarding/profile');
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
            onClick={() => navigate('/onboarding/profile')}
            className="flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-[#0f131d] border border-[#232b3e] text-slate-300 hover:text-white hover:bg-[#1a2030] text-xs font-semibold transition-colors"
          >
            <Github className="w-4 h-4 text-white" /> GitHub
          </button>
          <button
            type="button"
            onClick={handleGoogleClick}
            disabled={isGoogleLoading}
            className="flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-[#0f131d] border border-[#232b3e] text-slate-300 hover:text-white hover:bg-[#1a2030] text-xs font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGoogleLoading ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Signing up...</>
            ) : (
              <><Chrome className="w-4 h-4 text-rose-400" /> Google</>
            )}
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
            placeholder="e.g. DD Savaliya"
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
            placeholder="e.g. ddsavaliya2006@gmail.com"
            required
          />

          <PasswordInput
            label="Password"
            id="signup-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={fieldErrors.password}
            placeholder="Create password (min. 6 characters)"
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
