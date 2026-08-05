import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { OnboardingProvider } from './context/OnboardingContext';
import Home from './pages/Home';
import Auth from './pages/Auth';
import OnboardingDomain from './pages/OnboardingDomain';
import OnboardingDetails from './pages/OnboardingDetails';
import OnboardingProfiles from './pages/OnboardingProfiles';
import Report from './pages/Report';

export default function App() {
  return (
    <OnboardingProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/onboarding/domain" element={<OnboardingDomain />} />
          <Route path="/onboarding/details" element={<OnboardingDetails />} />
          <Route path="/onboarding/profiles" element={<OnboardingProfiles />} />
          <Route path="/report" element={<Report />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </OnboardingProvider>
  );
}
