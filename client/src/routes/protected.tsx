import { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../components/auth';

export const ProtectedAuthRoute: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { authorized } = useAuth();
  const location = useLocation();

  if (!authorized) {
    return <Navigate to="/restricted" state={{ from: location }} replace />;
  }

  return children;
};

export const ProtectedNonAuthRoute: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { authorized } = useAuth();
  const location = useLocation();

  if (authorized) {
    return <Navigate to="/inbox" state={{ from: location }} replace />;
  }

  return children;
};