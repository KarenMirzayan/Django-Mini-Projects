import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import ResumeUpload from '../components/ResumeUpload';
import { AuthContext } from '../App';

interface Resume {
  resume_id: string;
  score: number;
}

interface Job {
  job_id: number;
  title: string;
  description: string;
  skills_required: { skills: string[] };
  created_at: string;
  recruiter_id?: number;
}

const Dashboard: React.FC = () => {
  const { token } = useContext(AuthContext);
  const navigate = useNavigate();
  const [role, setRole] = useState<string | null>(null);
  const [userId, setUserId] = useState<number | null>(null); // New state for user ID
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [allJobs, setAllJobs] = useState<Job[]>([]);
  const [jobForm, setJobForm] = useState({ title: '', description: '', skills: '' });
  const [selectedJobId, setSelectedJobId] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!token) {
        setError('Please log in to access the dashboard');
        setLoading(false);
        return;
      }

      try {
        // Fetch user role and ID
        const userResponse = await axios.get('http://localhost:8000/api/user/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const userRole = userResponse.data.role;
        const currentUserId = userResponse.data.id; // Store user ID
        setRole(userRole);
        setUserId(currentUserId);

        // Fetch all job listings
        const allJobsResponse = await axios.get('http://localhost:8000/api/job/list/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setAllJobs(allJobsResponse.data);

        // Fetch user-specific data
        if (userRole === 'job_seeker') {
          const resumeResponse = await axios.get('http://localhost:8000/api/resumes/', {
            headers: { Authorization: `Bearer ${token}` },
          });
          setResumes(resumeResponse.data);
        } else if (userRole === 'recruiter') {
          const myJobsResponse = await axios.get('http://localhost:8000/api/job/list/', {
            headers: { Authorization: `Bearer ${token}` },
            params: { recruiter_id: currentUserId },
          });
          setJobs(myJobsResponse.data);
        }
        setLoading(false);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to load dashboard data');
        setLoading(false);
      }
    };
    fetchData();
  }, [token]);

  const handleUploadSuccess = (resumeId: string) => {
    setTimeout(() => navigate(`/resume/${resumeId}`), 2000);
  };

  const handleJobSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    try {
      const skillsArray = jobForm.skills.split(',').map((skill) => skill.trim());
      const response = await axios.post(
        'http://localhost:8000/api/job/create/',
        {
          title: jobForm.title,
          description: jobForm.description,
          skills_required: { skills: skillsArray },
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setJobs([...jobs, response.data]);
      setAllJobs([...allJobs, response.data]);
      setJobForm({ title: '', description: '', skills: '' });
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create job');
    }
  };

  if (loading) return <div className="container mx-auto p-4 text-center text-gray-600">Loading...</div>;
  if (error) return <div className="container mx-auto p-4 text-center text-red-600">{error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Dashboard</h1>

      {role === 'job_seeker' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">Upload Resume</h2>
            <div className="mb-4">
              <label htmlFor="job-select" className="block text-gray-600 mb-2">
                Select Job Listing (Optional)
              </label>
              <select
                id="job-select"
                value={selectedJobId || ''}
                onChange={(e) => setSelectedJobId(e.target.value || undefined)}
                className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">No job selected</option>
                {allJobs.map((job) => (
                  <option key={job.job_id} value={job.job_id.toString()}>
                    {job.title}
                  </option>
                ))}
              </select>
            </div>
            <ResumeUpload jobId={selectedJobId} onUploadSuccess={handleUploadSuccess} />
          </div>

          {resumes.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4 text-gray-700">Your Resumes</h2>
              <ul className="space-y-2">
                {resumes.map((resume) => (
                  <li key={resume.resume_id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <span className="text-gray-600">Resume ID: {resume.resume_id}</span>
                    <div className="flex space-x-2">
                      <span className="text-gray-500">Score: {resume.score}</span>
                      <button
                        onClick={() => navigate(`/resume/${resume.resume_id}`)}
                        className="text-blue-600 hover:underline"
                      >
                        View Details
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {role === 'recruiter' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">Create Job Listing</h2>
            <form onSubmit={handleJobSubmit} className="space-y-4">
              <input
                type="text"
                placeholder="Job Title"
                value={jobForm.title}
                onChange={(e) => setJobForm({ ...jobForm, title: e.target.value })}
                className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <textarea
                placeholder="Job Description"
                value={jobForm.description}
                onChange={(e) => setJobForm({ ...jobForm, description: e.target.value })}
                className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={4}
              />
              <input
                type="text"
                placeholder="Skills (comma-separated, e.g., Python, SQL)"
                value={jobForm.skills}
                onChange={(e) => setJobForm({ ...jobForm, skills: e.target.value })}
                className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 transition"
              >
                Create Job
              </button>
            </form>
          </div>

          {jobs.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4 text-gray-700">Your Job Listings</h2>
              <ul className="space-y-2">
                {jobs.map((job) => (
                  <li key={job.job_id} className="p-2 bg-gray-50 rounded">
                    <h3 className="text-lg font-medium text-gray-800">{job.title}</h3>
                    <p className="text-gray-600">{job.description}</p>
                    <p className="text-gray-500">
                      <strong>Skills:</strong> {job.skills_required.skills.join(', ')}
                    </p>
                    <p className="text-gray-400 text-sm">
                      Created: {new Date(job.created_at).toLocaleDateString()}
                    </p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* All Job Listings Section */}
      <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">All Job Listings</h2>
        {allJobs.length > 0 ? (
          <ul className="space-y-4">
            {allJobs.map((job) => (
              <li key={job.job_id} className="p-4 bg-gray-50 rounded-lg shadow-sm">
                <h3 className="text-lg font-medium text-gray-800">{job.title}</h3>
                <p className="text-gray-600">{job.description}</p>
                <p className="text-gray-500">
                  <strong>Skills:</strong> {job.skills_required.skills.join(', ')}
                </p>
                <p className="text-gray-400 text-sm">
                  Created: {new Date(job.created_at).toLocaleDateString()}
                </p>
                {role === 'recruiter' && job.recruiter_id === userId && (
                  <span className="inline-block mt-2 bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                    Your Listing
                  </span>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">No job listings available</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;