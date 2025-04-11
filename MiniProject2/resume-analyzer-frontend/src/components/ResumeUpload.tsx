// src/components/ResumeUpload.tsx
import React, { useCallback, useContext } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { AuthContext } from '../App';

interface ResumeUploadProps {
  jobId?: string;
  onUploadSuccess: (resumeId: string) => void;
}

const ResumeUpload: React.FC<ResumeUploadProps> = ({ jobId, onUploadSuccess }) => {
  const { token } = useContext(AuthContext);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      const formData = new FormData();
      formData.append('file', file);
      if (jobId) formData.append('job_id', jobId);

      try {
        const response = await axios.post('http://localhost:8000/api/resume/upload/', formData, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
        });
        onUploadSuccess(response.data.resume_id);
      } catch (error: any) {
        console.error('Upload failed:', error.response?.data);
      }
    },
    [jobId, onUploadSuccess, token]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
  });

  return (
    <div
      {...getRootProps()}
      className={`p-6 border-2 border-dashed rounded-lg text-center ${
        isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
      }`}
    >
      <input {...getInputProps()} />
      {isDragActive ? (
        <p className="text-blue-500">Drop the resume here...</p>
      ) : (
        <p className="text-gray-600">Drag & drop a resume (PDF), or click to select</p>
      )}
    </div>
  );
};

export default ResumeUpload;