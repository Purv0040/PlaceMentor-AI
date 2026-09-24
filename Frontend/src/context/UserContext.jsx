import React, { createContext, useContext, useState } from 'react';
import { mockUser } from '../data/mockUser';

const UserContext = createContext(null);

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(mockUser);

  const updateUserProfile = (newDetails) => {
    setUser(prev => ({
      ...prev,
      ...newDetails,
      // Merge nested objects cleanly
      preferences: { ...prev.preferences, ...(newDetails.preferences || {}) }
    }));
  };

  return (
    <UserContext.Provider value={{ user, updateUserProfile }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);
