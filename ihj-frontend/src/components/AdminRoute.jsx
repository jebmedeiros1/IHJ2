import { Navigate } from 'react-router-dom';
import { isAuthenticated, getUserInfo } from '@/lib/auth';

export default function AdminRoute({ children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  const user = getUserInfo();
  if (!user || user.access_level !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}
