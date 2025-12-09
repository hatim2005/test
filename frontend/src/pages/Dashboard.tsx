import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface CV {
  id: string;
  title: string;
  email: string;
  phone: string;
  summary: string;
  createdAt: string;
}

const Dashboard: React.FC = () => {
  const [cvs, setCvs] = useState<CV[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [userName, setUserName] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        const response = await fetch('http://localhost:5000/api/users/me', {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch user data');
        }

        const data = await response.json();
        setUserName(data.name);
        setCvs(data.cvs || []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const handleCreateCV = () => {
    navigate('/create-cv');
  };

  const handleEditCV = (cvId: string) => {
    navigate(`/edit-cv/${cvId}`);
  };

  const handleDeleteCV = async (cvId: string) => {
    if (!confirm('Are you sure you want to delete this CV?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/cvs/${cvId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        throw new Error('Failed to delete CV');
      }

      setCvs(cvs.filter((cv) => cv.id !== cvId));
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-md">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">CV Library</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">Welcome, {userName}</span>
            <button
              onClick={handleLogout}
              className="btn-secondary"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold text-gray-800">My CVs</h2>
          <button
            onClick={handleCreateCV}
            className="btn-primary"
          >
            Create New CV
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {cvs.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 text-lg mb-4">No CVs created yet</p>
            <button
              onClick={handleCreateCV}
              className="btn-primary"
            >
              Create Your First CV
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cvs.map((cv) => (
              <div key={cv.id} className="card">
                <h3 className="text-xl font-bold text-gray-800 mb-2">{cv.title}</h3>
                <p className="text-gray-600 mb-2">Email: {cv.email}</p>
                <p className="text-gray-600 mb-4">Phone: {cv.phone}</p>
                <p className="text-gray-500 text-sm mb-4">
                  Created: {new Date(cv.createdAt).toLocaleDateString()}
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEditCV(cv.id)}
                    className="btn-secondary flex-1"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteCV(cv.id)}
                    className="btn-danger flex-1"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
