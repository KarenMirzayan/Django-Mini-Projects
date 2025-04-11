import React, { useEffect, useState, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AuthContext } from '../App';
interface ResumeAnalysis {
  skills: string[];
  formatting: boolean;
  word_count: number;
  skill_density: number;
  suggestions: string[];
  missing_skills: string[];
  score: number;
}

interface ResumeData {
  resume_id: string;
  user_id: number;
  analysis: ResumeAnalysis;
  score: number;
}

const ResumeDetail: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>(); // Get resumeId from URL
  const { token } = useContext(AuthContext); // Access auth token
  const navigate = useNavigate();
  const [resume, setResume] = useState<ResumeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch resume data on mount
  useEffect(() => {
    const fetchResume = async () => {
      if (!token) {
        setError('Please log in to view resume details');
        setLoading(false);
        return;
      }

      if (!resumeId) {
        setError('Invalid resume ID');
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`http://localhost:8000/api/resume/${resumeId}/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setResume(response.data);
        setLoading(false);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to load resume details');
        setLoading(false);
      }
    };
    fetchResume();
  }, [resumeId, token]);

  // Handle navigation back to dashboard
  const handleBack = () => {
    navigate('/dashboard');
  };

  if (loading) {
    return <div className="container mx-auto p-4 text-center text-gray-600">Loading...</div>;
  }

  if (error) {
    return <div className="container mx-auto p-4 text-center text-red-600">{error}</div>;
  }

  if (!resume) {
    return <div className="container mx-auto p-4 text-center text-red-600">Resume not found</div>;
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Resume Analysis</h1>
        <button
          onClick={handleBack}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
        >
          Back to Dashboard
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md space-y-6">
        {/* Overview Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-gray-50 rounded">
            <h2 className="text-lg font-semibold text-gray-700">Score</h2>
            <p className="text-2xl font-bold text-blue-600">{resume.score.toFixed(1)}/100</p>
          </div>
          <div className="p-4 bg-gray-50 rounded">
            <h2 className="text-lg font-semibold text-gray-700">Word Count</h2>
            <p className="text-xl text-gray-600">{resume.analysis.word_count}</p>
          </div>
          <div className="p-4 bg-gray-50 rounded">
            <h2 className="text-lg font-semibold text-gray-700">Skill Density</h2>
            <p className="text-xl text-gray-600">{(resume.analysis.skill_density * 100).toFixed(1)}%</p>
          </div>
        </div>

        {/* Skills Section */}
        <div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Extracted Skills</h2>
          <div className="flex flex-wrap gap-2">
            {resume.analysis.skills.length > 0 ? (
              resume.analysis.skills.map((skill, index) => (
                <span
                  key={index}
                  className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm"
                >
                  {skill}
                </span>
              ))
            ) : (
              <p className="text-gray-500">No skills extracted</p>
            )}
          </div>
        </div>

        {/* Missing Skills Section */}
        <div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Missing Skills</h2>
          <div className="flex flex-wrap gap-2">
            {resume.analysis.missing_skills.length > 0 ? (
              resume.analysis.missing_skills.map((skill, index) => (
                <span
                  key={index}
                  className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm"
                >
                  {skill}
                </span>
              ))
            ) : (
              <p className="text-gray-500">No missing skills identified</p>
            )}
          </div>
        </div>

        {/* Suggestions Section */}
        <div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Suggestions</h2>
          {resume.analysis.suggestions.length > 0 ? (
            <ul className="list-disc pl-5 text-gray-600 space-y-1">
              {resume.analysis.suggestions.map((suggestion, index) => (
                <li key={index}>{suggestion}</li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No suggestions available</p>
          )}
        </div>

        {/* Formatting Feedback */}
        <div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Formatting</h2>
          <p className={resume.analysis.formatting ? 'text-green-600' : 'text-red-600'}>
            {resume.analysis.formatting
              ? 'Well-formatted resume'
              : 'Formatting issues detected'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ResumeDetail;