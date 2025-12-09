import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { cvAPI } from '../utils/api';

const CreateCV: React.FC = () => {
  const [formData, setFormData] = useState({
    title: '',
    fullName: '',
    email: '',
    phone: '',
    summary: '',
    experience: '',
    education: '',
    skills: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const cvData = {
        title: formData.title,
        fullName: formData.fullName,
        email: formData.email,
        phone: formData.phone,
        summary: formData.summary,
        experience: formData.experience,
        education: formData.education,
        skills: formData.skills.split(',').map((s) => s.trim()),
      };

      await cvAPI.create(cvData);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Create New CV</h1>
        <p className="text-gray-600 mb-8">Fill in your information to create a professional CV</p>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">CV Title</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
                className="input-field"
                placeholder="e.g., Senior Developer CV"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
              <input
                type="text"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                required
                className="input-field"
                placeholder="John Doe"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="input-field"
                placeholder="john@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                required
                className="input-field"
                placeholder="+1 (555) 123-4567"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Professional Summary</label>
            <textarea
              name="summary"
              value={formData.summary}
              onChange={handleChange}
              required
              className="input-field"
              rows={4}
              placeholder="Brief overview of your professional background..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Experience</label>
            <textarea
              name="experience"
              value={formData.experience}
              onChange={handleChange}
              required
              className="input-field"
              rows={5}
              placeholder="List your work experience..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Education</label>
            <textarea
              name="education"
              value={formData.education}
              onChange={handleChange}
              required
              className="input-field"
              rows={4}
              placeholder="List your educational background..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Skills (comma separated)</label>
            <textarea
              name="skills"
              value={formData.skills}
              onChange={handleChange}
              required
              className="input-field"
              rows={3}
              placeholder="JavaScript, React, TypeScript, Node.js..."
            />
          </div>

          <div className="flex gap-4 pt-6">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating CV...' : 'Create CV'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="flex-1 btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateCV;
