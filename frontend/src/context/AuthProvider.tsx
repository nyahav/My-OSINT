import { createContext, useState, ReactNode, useEffect } from 'react';
import { fetchUserDetails } from '../services/authService';

interface User {
  username: string;
  email: string;
  admin: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('access_token'));

  const login = async (token: string) => {
    localStorage.setItem('access_token', token);
    setToken(token);

    try {
      const userDetails = await fetchUserDetails(token);
      setUser(userDetails);
    } catch (err) {
      console.error('Failed to fetch user details:', err);
      logout();
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    setToken(null);
  };

  useEffect(() => {
  const storedToken = localStorage.getItem("access_token");
  if (storedToken) {
    setToken(storedToken);
    fetchUserDetails(storedToken)
      .then(setUser)
      .catch(() => logout())
      .finally(() => setIsAuthLoading(false));
  } else {
    setIsAuthLoading(false); 
  }
}, []);

  if (isAuthLoading) {
    return <p>Checking authentication...</p>; 
  }
  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
