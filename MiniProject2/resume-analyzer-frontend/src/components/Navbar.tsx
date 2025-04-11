import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';

const Navbar: React.FC = () => {
  const { token, setToken } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setToken(null);
    navigate('/login');
  };

  return (
    <nav className="bg-blue-600 p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-white text-xl font-bold">Resume Analyzer</Link>
        <div className="space-x-4">
          {!token ? (
            <>
              <Link to="/register" className="text-white hover:text-gray-200">Register</Link>
              <Link to="/login" className="text-white hover:text-gray-200">Login</Link>
            </>
          ) : (
            <>
              <Link to="/dashboard" className="text-white hover:text-gray-200">Dashboard</Link>
              <button onClick={handleLogout} className="text-white hover:text-gray-200">
                Logout
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;