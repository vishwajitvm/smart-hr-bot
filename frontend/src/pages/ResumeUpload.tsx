import React, { useState, useEffect } from "react";
import "./css/ResumeUpload.css";
import {
  uploadResume,
  submitCandidateDetails,
  fetchJobPositions,
} from "../services/api";

interface ResumeData {
  name: string;
  email: string;
  location: string;
  experience: string;
  skills: string[];
  position: string;
}

const ResumeUpload: React.FC = () => {
  const [resumeData, setResumeData] = useState<ResumeData>({
    name: "",
    email: "",
    location: "",
    experience: "",
    skills: [],
    position: "",
  });

  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [positions, setPositions] = useState<string[]>([]);

  /* -------------------------------------------------------------------------- */
  /*                             Fetch Job Positions                            */
  /* -------------------------------------------------------------------------- */
  useEffect(() => {
    const loadPositions = async () => {
      try {
        const response = await fetchJobPositions();
        setPositions(response.data || []);
      } catch (error) {
        console.error("Failed to fetch job positions:", error);
        // fallback if API fails
        setPositions([
          "Software Engineer",
          "Frontend Developer",
          "Backend Developer",
          "HR Manager",
        ]);
      }
    };

    loadPositions();
  }, []);

  /* -------------------------------------------------------------------------- */
  /*                               File Handling                                */
  /* -------------------------------------------------------------------------- */
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please upload a resume file.");
      return;
    }

    try {
      setLoading(true);
      const response = await uploadResume(file);
      setResumeData((prev) => ({
        ...prev,
        ...response.data, // backend should return {name, email, skills...}
      }));
    } catch (error) {
      console.error("Error uploading resume:", error);
      alert("Failed to parse resume.");
    } finally {
      setLoading(false);
    }
  };

  /* -------------------------------------------------------------------------- */
  /*                             Form Input Handling                            */
  /* -------------------------------------------------------------------------- */
  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setResumeData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSkillsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setResumeData((prev) => ({
      ...prev,
      skills: value.split(",").map((s) => s.trim()),
    }));
  };

  /* -------------------------------------------------------------------------- */
  /*                                 Submit Form                                */
  /* -------------------------------------------------------------------------- */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await submitCandidateDetails(resumeData);
      alert("Application submitted successfully!");
    } catch (error) {
      console.error("Error submitting application:", error);
      alert("Failed to submit application.");
    }
  };

  /* -------------------------------------------------------------------------- */
  /*                                    JSX                                     */
  /* -------------------------------------------------------------------------- */
  return (
    <div className="max-w-2xl mx-auto p-6 bg-white shadow rounded">
      <h2 className="text-xl font-bold mb-4">Resume Upload & Application</h2>

      {/* File Upload */}
      <div className="mb-4">
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleFileChange}
          className="mb-2"
        />
        <button
          onClick={handleUpload}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          {loading ? "Parsing..." : "Upload & Autofill"}
        </button>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Dropdown for Position */}
        <div>
          <label className="block font-medium">Position Applying For</label>
          <select
            name="position"
            value={resumeData.position}
            onChange={handleChange}
            className="w-full border p-2 rounded"
          >
            <option value="">Select Position</option>
            {positions.map((pos) => (
              <option key={pos} value={pos}>
                {pos}
              </option>
            ))}
          </select>
        </div>

        {/* Name */}
        <div>
          <label className="block font-medium">Full Name</label>
          <input
            type="text"
            name="name"
            value={resumeData.name}
            onChange={handleChange}
            className="w-full border p-2 rounded"
          />
        </div>

        {/* Email */}
        <div>
          <label className="block font-medium">Email</label>
          <input
            type="email"
            name="email"
            value={resumeData.email}
            onChange={handleChange}
            className="w-full border p-2 rounded"
          />
        </div>

        {/* Location */}
        <div>
          <label className="block font-medium">Location</label>
          <input
            type="text"
            name="location"
            value={resumeData.location}
            onChange={handleChange}
            className="w-full border p-2 rounded"
          />
        </div>

        {/* Experience */}
        <div>
          <label className="block font-medium">Experience</label>
          <textarea
            name="experience"
            value={resumeData.experience}
            onChange={handleChange}
            className="w-full border p-2 rounded"
          ></textarea>
        </div>

        {/* Skills */}
        <div>
          <label className="block font-medium">Skills (comma separated)</label>
          <input
            type="text"
            value={resumeData.skills.join(", ")}
            onChange={handleSkillsChange}
            className="w-full border p-2 rounded"
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          Submit Application
        </button>
      </form>
    </div>
  );
};

export default ResumeUpload;
