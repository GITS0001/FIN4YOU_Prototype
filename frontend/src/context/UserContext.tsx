import React, { createContext, useContext, useState, useCallback } from 'react';

// Static prototype user (used to be an array for demo switching)
export const DEFAULT_USER = { id: 'user_28', label: 'Aditya', currency: 'INR' };

export const DEFAULT_USER_ID = 'user_28';

interface UserContextValue {
  selectedUserId: string;
  setSelectedUserId: (id: string) => void;
}

const UserContext = createContext<UserContextValue>({
  selectedUserId: DEFAULT_USER_ID,
  setSelectedUserId: () => {},
});

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [selectedUserId, setSelectedUserIdState] = useState<string>(() => {
    // Restore from localStorage for persistence across refreshes
    return localStorage.getItem('fin4you_selected_user') || DEFAULT_USER_ID;
  });

  const setSelectedUserId = useCallback((id: string) => {
    localStorage.setItem('fin4you_selected_user', id);
    setSelectedUserIdState(id);
  }, []);

  return (
    <UserContext.Provider value={{ selectedUserId, setSelectedUserId }}>
      {children}
    </UserContext.Provider>
  );
};

export const useSelectedUser = () => useContext(UserContext);
