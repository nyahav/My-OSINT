// components/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import  useAuth  from '../../context/useAuth'; // adjust path as needed

const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
