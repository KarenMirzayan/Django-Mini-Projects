import React, { useEffect, useState, useContext } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AuthContext } from '../App';

const VerifyEmail: React.FC = () => {
  const [searchParams] = useSearchParams(); // Get query params from URL
  const { setToken } = useContext(AuthContext);
  const navigate = useNavigate();
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyEmail = async () => {
      const token = searchParams.get('token');
      if (!token) {
        setError('No verification token provided');
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get('http://localhost:8000/api/verify-email', {
          params: { token },
        });

        const { access_token, refresh_token } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        setToken(access_token); // Update context

        setMessage(response.data.message);
        setTimeout(() => navigate('/login'), 2000);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to verify email');
        setLoading(false);
      }
    };

    verifyEmail();
  }, [searchParams, setToken, navigate]);

  if (loading) {
    return (
      <div className="container mx-auto p-4 text-center">
        <p className="text-gray-600">Verifying your email...</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-md">
      <h1 className="text-2xl font-bold mb-4 text-gray-800">Email Verification</h1>
      {message && (
        <div className="p-4 bg-green-100 text-green-800 rounded-lg">
          <p>{message}</p>
          <p className="mt-2">Redirecting to login...</p>
        </div>
      )}
      {error && (
        <div className="p-4 bg-red-100 text-red-800 rounded-lg">
          <p>{error}</p>
          <button
            onClick={() => navigate('/register')}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
          >
            Back to Register
          </button>
        </div>
      )}
    </div>
  );
};

export default VerifyEmail;