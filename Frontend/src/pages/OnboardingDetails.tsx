import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useOnboarding } from '../context/OnboardingContext';
import {
  Sparkles,
  ArrowLeft,
  ArrowRight,
  User,
  Mail,
  GraduationCap,
  Building2,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';

const BRANCH_OPTIONS = ['CE', 'CSE', 'IT', 'AIML', 'BSE IT', 'MCA', 'BCA'] as const;

export const OnboardingDetails: React.FC = () => {
  const navigate = useNavigate();
  const { academicDetails, setAcademicDetails, selectedDomain } = useOnboarding();

  // Local state initialized with context / localStorage
  const [studentName, setStudentName] = useState(academicDetails.studentName || '');
  const [email, setEmail] = useState(academicDetails.email || '');
  const [branch, setBranch] = useState(academicDetails.branch || 'CSE');
  const [collegeName, setCollegeName] = useState(academicDetails.collegeName || '');

  const [errors, setErrors] = useState<{
    studentName?: string;
    email?: string;
    branch?: string;
    collegeName?: string;
  }>({});

  // Prefill from auth user if available and empty
  useEffect(() => {
    if (!studentName || !email) {
      const savedUser = localStorage.getItem('placeMentorUser');
      if (savedUser) {
        try {
          const userObj = JSON.parse(savedUser);
          if (userObj.name && !studentName) setStudentName(userObj.name);
          if (userObj.email && !email) setEmail(userObj.email);
        } catch {
          // ignore error
        }
      }
    }
  }, []);

  const validateEmail = (val: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
  };

  const handleNext = (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: {
      studentName?: string;
      email?: string;
      branch?: string;
      collegeName?: string;
    } = {};

    if (!studentName.trim()) {
      newErrors.studentName = 'Student Name is required';
    }

    if (!email.trim()) {
      newErrors.email = 'Email Address is required';
    } else if (!validateEmail(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!branch) {
      newErrors.branch = 'Please select your academic branch';
    }

    if (!collegeName.trim()) {
      newErrors.collegeName = 'College Name is required';
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      // Save data to Context
      setAcademicDetails({
        studentName: studentName.trim(),
        email: email.trim(),
        branch,
        collegeName: collegeName.trim(),
      });

      // Navigate to /onboarding/profiles
      navigate('/onboarding/profiles');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between p-4 sm:p-6 md:p-10 antialiased selection:bg-indigo-500 selection:text-white">
      {/* Top Header Step Indicator */}
      <header className="w-full max-w-2xl mx-auto flex items-center justify-between pb-6">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-indigo-600 text-white rounded-xl shadow-sm">
            <Sparkles className="w-5 h-5" />
          </div>
          <span className="font-bold text-slate-900 text-base tracking-tight">
            PlaceMentor AI
          </span>
        </div>

        {/* Step Counter */}
        <div className="flex items-center gap-2 bg-indigo-50/80 px-3.5 py-1.5 rounded-full border border-indigo-100 text-xs font-semibold text-indigo-700">
          <span>Step 2 of 3</span>
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
          <span className="text-slate-600">Student Details</span>
        </div>
      </header>

      {/* Main Container Card */}
      <main className="w-full max-w-2xl mx-auto my-auto">
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-md p-6 sm:p-8 md:p-10">
          {/* Back Button */}
          <Link
            to="/onboarding/domain"
            id="back-to-domain-link"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Domain Selection</span>
          </Link>

          {/* Form Header */}
          <div className="mb-8">
            <h1 id="details-heading" className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Student Details
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              Provide your academic background to help us tailor placement readiness reports.
              {selectedDomain && (
                <span className="ml-1 text-indigo-600 font-medium">
                  (Selected Domain: {selectedDomain})
                </span>
              )}
            </p>
          </div>

          {/* Form */}
          <form id="student-details-form" onSubmit={handleNext} noValidate className="space-y-5">
            {/* Student Name */}
            <div>
              <label htmlFor="student-name-input" className="block text-xs font-semibold text-slate-700 mb-1.5">
                Student Name <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <User className="w-4 h-4" />
                </div>
                <input
                  id="student-name-input"
                  type="text"
                  value={studentName}
                  onChange={(e) => {
                    setStudentName(e.target.value);
                    if (errors.studentName) setErrors((prev) => ({ ...prev, studentName: undefined }));
                  }}
                  placeholder="e.g. Alex Rivera"
                  className={`w-full pl-10 pr-3.5 py-2.5 text-sm bg-slate-50 border ${
                    errors.studentName ? 'border-red-400 bg-red-50/20' : 'border-slate-200'
                  } rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder:text-slate-400`}
                />
              </div>
              {errors.studentName && (
                <p className="flex items-center gap-1 text-xs text-red-500 mt-1.5 font-medium">
                  <AlertCircle className="w-3.5 h-3.5" />
                  <span>{errors.studentName}</span>
                </p>
              )}
            </div>

            {/* Email Address */}
            <div>
              <label htmlFor="email-input" className="block text-xs font-semibold text-slate-700 mb-1.5">
                Email Address <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  id="email-input"
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (errors.email) setErrors((prev) => ({ ...prev, email: undefined }));
                  }}
                  placeholder="alex.rivera@university.edu"
                  className={`w-full pl-10 pr-3.5 py-2.5 text-sm bg-slate-50 border ${
                    errors.email ? 'border-red-400 bg-red-50/20' : 'border-slate-200'
                  } rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder:text-slate-400`}
                />
              </div>
              {errors.email && (
                <p className="flex items-center gap-1 text-xs text-red-500 mt-1.5 font-medium">
                  <AlertCircle className="w-3.5 h-3.5" />
                  <span>{errors.email}</span>
                </p>
              )}
            </div>

            {/* Branch Dropdown */}
            <div>
              <label htmlFor="branch-select" className="block text-xs font-semibold text-slate-700 mb-1.5">
                Academic Branch <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <GraduationCap className="w-4 h-4" />
                </div>
                <select
                  id="branch-select"
                  value={branch}
                  onChange={(e) => {
                    setBranch(e.target.value);
                    if (errors.branch) setErrors((prev) => ({ ...prev, branch: undefined }));
                  }}
                  className={`w-full pl-10 pr-9 py-2.5 text-sm bg-slate-50 border ${
                    errors.branch ? 'border-red-400 bg-red-50/20' : 'border-slate-200'
                  } rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 cursor-pointer appearance-none`}
                >
                  {BRANCH_OPTIONS.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 pr-3.5 flex items-center pointer-events-none text-slate-400">
                  <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
                    <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
                  </svg>
                </div>
              </div>
              {errors.branch && (
                <p className="flex items-center gap-1 text-xs text-red-500 mt-1.5 font-medium">
                  <AlertCircle className="w-3.5 h-3.5" />
                  <span>{errors.branch}</span>
                </p>
              )}
            </div>

            {/* College Name */}
            <div>
              <label htmlFor="college-name-input" className="block text-xs font-semibold text-slate-700 mb-1.5">
                College Name <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Building2 className="w-4 h-4" />
                </div>
                <input
                  id="college-name-input"
                  type="text"
                  value={collegeName}
                  onChange={(e) => {
                    setCollegeName(e.target.value);
                    if (errors.collegeName) setErrors((prev) => ({ ...prev, collegeName: undefined }));
                  }}
                  placeholder="e.g. Stanford University / Institute of Technology"
                  className={`w-full pl-10 pr-3.5 py-2.5 text-sm bg-slate-50 border ${
                    errors.collegeName ? 'border-red-400 bg-red-50/20' : 'border-slate-200'
                  } rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder:text-slate-400`}
                />
              </div>
              {errors.collegeName && (
                <p className="flex items-center gap-1 text-xs text-red-500 mt-1.5 font-medium">
                  <AlertCircle className="w-3.5 h-3.5" />
                  <span>{errors.collegeName}</span>
                </p>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-6 border-t border-slate-100 mt-8">
              <Link
                to="/onboarding/domain"
                id="back-btn"
                className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-slate-600 bg-slate-100 rounded-xl hover:bg-slate-200 transition-all"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </Link>

              <button
                id="next-profiles-btn"
                type="submit"
                className="inline-flex items-center gap-2 px-7 py-2.5 text-sm font-semibold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 active:bg-indigo-800 transition-all shadow-sm hover:shadow-indigo-200 cursor-pointer"
              >
                <span>Next: Profiles & Resume</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full max-w-2xl mx-auto text-center py-4 text-xs text-slate-400">
        Placement Readiness Analyzer • Student Details Step
      </footer>
    </div>
  );
};

export default OnboardingDetails;
