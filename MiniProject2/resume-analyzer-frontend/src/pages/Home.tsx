// src/pages/Home.tsx
import React from 'react';

const Home: React.FC = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-gray-800">Welcome to Resume Analyzer</h1>
      <p className="mt-2 text-gray-600">Upload your resume or browse job listings.</p>
    </div>
  );
};

export default Home;