import React, { createContext, useContext, useState, useEffect } from 'react';

export interface AcademicDetails {
  studentName: string;
  email: string;
  branch: string;
  collegeName: string;
}

export interface ProfileLinks {
  githubUrl: string;
  leetcodeUrl: string;
  hackerRankUrl: string;
  linkedinUrl?: string;
  resumeFileName: string;
  resumeText: string;
  resumeMode: 'file' | 'text';
}

export interface ProfileAnalysis {
  github?: {
    repoCount?: number;
    reposCount?: number;
    topLanguages?: string[];
    summary?: string;
    highlights?: string[];
    contributionsThisYear?: number;
  };
  leetcode?: {
    solved?: {
      easy: number;
      medium: number;
      hard: number;
    };
    solvedCount?: number;
    topTags?: string[];
    contestRating?: number;
    badge?: string;
    topicBreakdown?: Record<string, number>;
  };
  hackerrank?: {
    badges?: string[];
    badgesCount?: number;
    topCategories?: string[];
    stars?: number;
    primarySkills?: string[];
  };
  linkedin?: {
    provided?: boolean;
    summary?: string;
    connections?: string;
    profileStrength?: string;
    endorsements?: string[];
  };
  resume?: {
    skillsDetected?: string[];
    experienceSummary?: string;
  };
}

export interface Recommendation {
  title: string;
  desc: string;
  priority: 'High' | 'Medium' | 'Low';
}

export interface MatchedSkill {
  skill: string;
  foundIn: string;
}

export interface MissingSkill {
  skill: string;
  reason: string;
}

export interface ReportData {
  id?: string;
  readinessScore: number;
  grade: string;
  matchedSkills: MatchedSkill[];
  missingSkills: MissingSkill[];
  comparisonSummary: string[];
  domainName: string;
  studentName: string;
  collegeName: string;
  branch: string;
  generatedAt: string;
  recommendations?: Recommendation[];
  projectSuggestions?: string[];
  profileAnalysis?: ProfileAnalysis;
}

interface OnboardingContextType {
  selectedDomain: string | null;
  setSelectedDomain: (domain: string) => void;
  academicDetails: AcademicDetails;
  setAcademicDetails: React.Dispatch<React.SetStateAction<AcademicDetails>>;
  profileLinks: ProfileLinks;
  setProfileLinks: React.Dispatch<React.SetStateAction<ProfileLinks>>;
  reportData: ReportData | null;
  setReportData: (report: ReportData) => void;
  resetOnboarding: () => void;
}

const defaultAcademicDetails: AcademicDetails = {
  studentName: '',
  email: '',
  branch: 'CSE',
  collegeName: '',
};

const defaultProfileLinks: ProfileLinks = {
  githubUrl: '',
  leetcodeUrl: '',
  hackerRankUrl: '',
  linkedinUrl: '',
  resumeFileName: '',
  resumeText: '',
  resumeMode: 'file',
};

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);

export const OnboardingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [selectedDomain, setSelectedDomainState] = useState<string | null>(() => {
    return localStorage.getItem('placeMentor_domain') || null;
  });

  const [academicDetails, setAcademicDetails] = useState<AcademicDetails>(() => {
    const saved = localStorage.getItem('placeMentor_academic');
    return saved ? JSON.parse(saved) : defaultAcademicDetails;
  });

  const [profileLinks, setProfileLinks] = useState<ProfileLinks>(() => {
    const saved = localStorage.getItem('placeMentor_profiles');
    return saved ? JSON.parse(saved) : defaultProfileLinks;
  });

  const [reportData, setReportDataState] = useState<ReportData | null>(() => {
    const saved = localStorage.getItem('placeMentor_report');
    return saved ? JSON.parse(saved) : null;
  });

  const setSelectedDomain = (domain: string) => {
    setSelectedDomainState(domain);
    localStorage.setItem('placeMentor_domain', domain);
  };

  const setReportData = (report: ReportData) => {
    setReportDataState(report);
    localStorage.setItem('placeMentor_report', JSON.stringify(report));
  };

  useEffect(() => {
    localStorage.setItem('placeMentor_academic', JSON.stringify(academicDetails));
  }, [academicDetails]);

  useEffect(() => {
    localStorage.setItem('placeMentor_profiles', JSON.stringify(profileLinks));
  }, [profileLinks]);

  const resetOnboarding = () => {
    setSelectedDomainState(null);
    setAcademicDetails(defaultAcademicDetails);
    setProfileLinks(defaultProfileLinks);
    setReportDataState(null);
    localStorage.removeItem('placeMentor_domain');
    localStorage.removeItem('placeMentor_academic');
    localStorage.removeItem('placeMentor_profiles');
    localStorage.removeItem('placeMentor_report');
  };

  return (
    <OnboardingContext.Provider
      value={{
        selectedDomain,
        setSelectedDomain,
        academicDetails,
        setAcademicDetails,
        profileLinks,
        setProfileLinks,
        reportData,
        setReportData,
        resetOnboarding,
      }}
    >
      {children}
    </OnboardingContext.Provider>
  );
};

export const useOnboarding = (): OnboardingContextType => {
  const context = useContext(OnboardingContext);
  if (!context) {
    throw new Error('useOnboarding must be used within an OnboardingProvider');
  }
  return context;
};
