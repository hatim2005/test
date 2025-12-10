import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { cvAPI } from '../utils/api';

const ViewCV: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [cv, setCV] = useState<any>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCV = async () => {
      if (!id) return;
      try {
        const data = await cvAPI.getById(id);
        setCV(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCV();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="max-w-2xl w-full bg-white rounded-lg shadow-md p-8">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Error Loading CV</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-primary"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!cv) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="max-w-2xl w-full bg-white rounded-lg shadow-md p-8">
          <p className="text-gray-600">CV not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-12">
        {/* Header */}
        <div className="border-b-2 border-gray-200 pb-8 mb-8">
          <h1 className="text-5xl font-bold text-gray-800 mb-2">{cv.fullName}</h1>
          <p className="text-lg text-gray-600 mb-4">{cv.title}</p>
          <div className="flex gap-6 text-gray-600">
            <span>Email: {cv.email}</span>
            <span>Phone: {cv.phone}</span>
          </div>
        </div>

        {/* Summary */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Professional Summary</h2>
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{cv.summary}</p>
        </div>

        {/* Experience */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Experience</h2>
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{cv.experience}</p>
        </div>

        {/* Education */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Education</h2>
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{cv.education}</p>
        </div>

        {/* Skills */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Skills</h2>
          <div className="flex flex-wrap gap-2">
            {Array.isArray(cv.skills) ? (
              cv.skills.map((skill: string, index: number) => (
                <span
                  key={index}
                  className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium"
                >
                  {skill}
                </span>
              ))
            ) : (
              <p className="text-gray-600">No skills listed</p>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4 pt-8 border-t-2 border-gray-200">
          <button
            onClick={() => navigate(`/edit-cv/${id}`)}
            className="flex-1 btn-primary"
          >
            Edit CV
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="flex-1 btn-secondary"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default ViewCV;
