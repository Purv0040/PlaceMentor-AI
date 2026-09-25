import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { UserProvider } from './context/UserContext';
import { AppProvider } from './context/AppContext';
import { PlanningProvider } from './context/PlanningContext';
import { OnboardingProvider } from './context/OnboardingContext';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { AppRoutes } from './routes/AppRoutes';

export function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <UserProvider>
            <AppProvider>
              <PlanningProvider>
                <OnboardingProvider>
                  <AppRoutes />
                </OnboardingProvider>
              </PlanningProvider>
            </AppProvider>
          </UserProvider>
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
