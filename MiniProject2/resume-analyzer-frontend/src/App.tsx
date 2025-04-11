// src/App.tsx
import React, { createContext, useState, Context } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Register from './pages/Register';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ResumeDetail from './pages/ResumeDetail';
import VerifyEmail from "./pages/VerifyEmail.tsx";

// Define the shape of the context
interface AuthContextType {
  token: string | null;
  setToken: (token: string | null) => void;
}

// Create and export the context
export const AuthContext: Context<AuthContextType> = createContext<AuthContextType>({
  token: null,
  setToken: () => {},
});

const App: React.FC = () => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));

  return (
    <AuthContext.Provider value={{ token, setToken }}>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-100">
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/resume/:resumeId" element={<ResumeDetail />} />
            <Route path="/verify-email" element={<VerifyEmail />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthContext.Provider>
  );
};

export default App;