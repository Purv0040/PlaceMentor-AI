import React, { createContext, useContext, useEffect, useState } from 'react';

const AppContext = createContext(null);

export const AppProvider = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem('placementor-theme') || 'dark');
  const [activeNotificationCount, setActiveNotificationCount] = useState(3);

  const toggleSidebar = () => setSidebarOpen(prev => !prev);
  const closeSidebar = () => setSidebarOpen(false);
  const toggleTheme = () => setTheme((currentTheme) => currentTheme === 'dark' ? 'light' : 'dark');

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('placementor-theme', theme);
  }, [theme]);

  return (
    <AppContext.Provider value={{
      sidebarOpen,
      toggleSidebar,
      closeSidebar,
      theme,
      setTheme,
      toggleTheme,
      activeNotificationCount
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
