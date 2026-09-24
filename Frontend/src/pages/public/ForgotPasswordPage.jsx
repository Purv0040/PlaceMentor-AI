import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Mail, ArrowLeft, CheckCircle2, Key } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Input } from '../../components/common/Input';
import { FormError } from '../../components/common/FormError';
import { Button } from '../../components/common/Button';

export const ForgotPasswordPage = () => {
  const { resetPassword } = useAuth();
  const [email, setEmail] = useState('alex.patel@charusat.edu.in');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      setError('Please enter a valid college email address.');
      return;
    }

    setIsLoading(true);
    try {
      await resetPassword(email);
      setIsLoading(false);
      setIsSubmitted(true);
    } catch (err) {
      setIsLoading(false);
      setError(err.message || 'Failed to send reset link. Please try again.');
    }
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center p-4 sm:p-6">
      <div className="w-full max-w-md p-6 sm:p-8 rounded-2xl bg-[#121624] border border-[#232b3e] shadow-2xl space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="w-10 h-10 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400 shadow-md">
            <Key className="w-5 h-5" />
          </div>
          <h2 className="text-2xl font-extrabold text-white">Reset your password</h2>
          <p className="text-xs text-slate-400">
            Enter your college email address to receive password reset instructions
          </p>
        </div>

        <FormError message={error} />

        {!isSubmitted ? (
          /* Form View */
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="College Email"
              id="forgot-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              icon={Mail}
              placeholder="alex.patel@charusat.edu.in"
              required
            />

            <Button
              type="submit"
              isLoading={isLoading}
              className="w-full"
              variant="primary"
            >
              Send Reset Link
            </Button>

            <div className="text-center pt-2">
              <NavLink
                to="/login"
                className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-4 h-4" /> Back to Login
              </NavLink>
            </div>
          </form>
        ) : (
          /* Success State View */
          <div className="space-y-4 text-center py-2">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mx-auto text-emerald-400">
              <CheckCircle2 className="w-6 h-6" />
            </div>

            <div className="space-y-1">
              <h3 className="text-lg font-bold text-white">Check your email</h3>
              <p className="text-xs text-slate-400 max-w-xs mx-auto leading-relaxed">
                We have sent password reset instructions to <span className="text-slate-200 font-semibold">{email}</span>.
              </p>
            </div>

            <div className="pt-4 space-y-3">
              <button
                type="button"
                onClick={() => setIsSubmitted(false)}
                className="text-xs text-indigo-400 hover:underline font-semibold block w-full"
              >
                Didn't receive email? Resend link
              </button>

              <NavLink
                to="/login"
                className="inline-flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-[#0f131d] border border-[#232b3e] text-slate-200 hover:text-white text-xs font-semibold transition-colors"
              >
                <ArrowLeft className="w-4 h-4" /> Return to Login
              </NavLink>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
