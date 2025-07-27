import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import BuscaCaracteristicas from './components/BuscaCaracteristicas';
import AnaliseSimilaridade from './components/AnaliseSimilaridade';
import ProtectedRoute from './components/ProtectedRoute';
import { isAuthenticated } from './lib/auth';
import './App.css';

// Configuração do React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* Rota de login */}
          <Route
            path="/login"
            element={
              isAuthenticated() ? <Navigate to="/dashboard" replace /> : <LoginForm />
            }
          />
          <Route
            path="/register"
            element={isAuthenticated() ? <Navigate to="/dashboard" replace /> : <RegisterForm />}
          />
          
          {/* Rotas protegidas */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="caracteristicas" element={<BuscaCaracteristicas />} />
            <Route path="similaridade" element={<AnaliseSimilaridade />} />
          </Route>
          
          {/* Redirecionamento padrão */}
          <Route 
            path="/" 
            element={
              <Navigate to={isAuthenticated() ? "/dashboard" : "/login"} replace />
            } 
          />
          
          {/* Rota 404 */}
          <Route 
            path="*" 
            element={
              <Navigate to={isAuthenticated() ? "/dashboard" : "/login"} replace />
            } 
          />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;

