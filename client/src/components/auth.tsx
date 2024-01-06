import { createContext, useState, useContext, useEffect, ReactNode } from 'react';


interface AuthContextType {
  authorized: boolean;
  setAuthorized: (authorized: boolean) => void;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [authorized, setAuthorized] = useState<boolean>(false);

  const checkAuthStatus = async () => {
    const response = await fetch('/api/auth/whoami');
    const data = await response.json();
    setAuthorized(data.auth);
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  return (
    <AuthContext.Provider value={{ authorized, setAuthorized }}>
      {children}
    </AuthContext.Provider>
  );
};