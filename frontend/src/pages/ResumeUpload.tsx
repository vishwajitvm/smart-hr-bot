import React, { useState, useEffect, type ReactNode } from "react";
import "./css/ResumeUpload.css";
import {
  uploadResume,
  submitCandidateDetails,
  fetchAllJobs
} from "../services/api";

interface ResumeData {
  name: string;
  email: string | null;
  phone: string | null;
  location: string | null;
  years_of_experience: string;
  skills: string[];
  interests: string[];
  experience_summary: string;
  position: string;
  job_id: string;
  resume_id: string | null;
  resume_url: string | null;
}

interface Job {
  id: string;
  title: string;
  department: string;
  location: string;
  workMode: string;
  type: string;
  experience: string;
  openings: number;
  salary: string;
  description: string;
  responsibilities: string;
  requirements: string;
  benefits: string;
  extraInfo?: ReactNode;
  status: number;
}

const ResumeUpload: React.FC = () => {
  const [resumeData, setResumeData] = useState<ResumeData>({
    name: "",
    email: "",
    phone: "",
    location: "",
    years_of_experience: "",
    skills: [],
    interests: [],
    experience_summary: "",
    position: "",
    job_id: "",
    resume_id: "",
    resume_url: ""

  });

  const [file, setFile] = useState<File | null>(null);
  const [filePreviewUrl, setFilePreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  // const [positions, setPositions] = useState<string[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [showDetails, setShowDetails] = useState(false);

  const [notification, setNotification] = useState<{
    message: string;
    type: "is-success" | "is-danger" | "is-warning" | "";
  }>({ message: "", type: "" });

  /* -------------------------------------------------------------------------- */
  /*                             Fetch Job Positions                            */
  /* -------------------------------------------------------------------------- */
  useEffect(() => {
    const loadJobs = async () => {
      try {
        const response = await fetchAllJobs();
        const activeJobs = (response.data || []).filter(
          (job: Job) => job.status === 1
        );
        setJobs(activeJobs);
      } catch (error) {
        console.error("Failed to fetch jobs:", error);
        setJobs([]);
      }
    };

    loadJobs();
  }, []);


  /* -------------------------------------------------------------------------- */
  /*                               File Handling                                */
  /* -------------------------------------------------------------------------- */
  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const uploadedFile = e.dataTransfer.files[0];
      setFile(uploadedFile);
      setFilePreviewUrl(URL.createObjectURL(uploadedFile));
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const uploadedFile = e.target.files[0];
      setFile(uploadedFile);
      setFilePreviewUrl(URL.createObjectURL(uploadedFile));
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setNotification({ message: "Please upload a resume file.", type: "is-warning" });
      // alert("Please upload a resume file.");
      return;
    }

    try {
      setLoading(true);
      const response = await uploadResume(file);

      setResumeData((prev) => ({
        ...prev,
        ...response.data, // fill with API response
      }));

      setNotification({ message: "Resume uploaded & parsed successfully!", type: "is-success" });

      if (response.data.download_url) {
        setFilePreviewUrl(response.data.download_url);
      }
    } catch (error) {
      console.error("Error uploading resume:", error);
      setNotification({ message: "Failed to parse resume.", type: "is-danger" });
      // alert("Failed to parse resume.");
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

  const handleTagInput = (
    e: React.KeyboardEvent<HTMLInputElement>,
    field: "skills" | "interests"
  ) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const value = (e.target as HTMLInputElement).value.trim();
      if (value && !resumeData[field].includes(value)) {
        setResumeData((prev) => ({
          ...prev,
          [field]: [...prev[field], value],
        }));
        (e.target as HTMLInputElement).value = "";
      }
    }
  };

  const removeTag = (field: "skills" | "interests", index: number) => {
    setResumeData((prev) => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index),
    }));
  };

  /* -------------------------------------------------------------------------- */
  /*                                 Submit Form                                */
  /* -------------------------------------------------------------------------- */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Validation
    if (!resumeData.job_id) {
      setNotification({ message: "Please select a job position.", type: "is-warning" });
      return;
    }
    // if (!resumeData.position) {
    //   setNotification({ message: "Position title missing. Please re-select a job.", type: "is-warning" });
    //   // alert("Position title missing. Please re-select a job.");
    //   return;
    // }
    if (!resumeData.name.trim()) {
      // alert("Full Name is required.");
      setNotification({ message: "Full Name is required.", type: "is-danger" });
      return;
    }
    if (!resumeData.email?.trim()) {
      // alert("Email is required.");
      setNotification({ message: "Email is required.", type: "is-danger" });
      return;
    }
    if (!resumeData.phone?.trim()) {
      // alert("Phone is required.");
      setNotification({ message: "Phone is required.", type: "is-danger" });
      return;
    }
    if (!resumeData.years_of_experience?.trim()) {
      // alert("Years of Experience is required.");
      setNotification({ message: "Years of Experience is required.", type: "is-danger" });
      return;
    }
    if (resumeData.skills.length === 0) {
      // alert("Please add at least one skill.");
      setNotification({ message: "Please add at least one skill.", type: "is-danger" });
      return;
    }
    try {
      const payload = {
        ...resumeData,
        email: resumeData.email || "",
        phone: resumeData.phone || "",
        location: resumeData.location || "",
        years_of_experience: resumeData.years_of_experience || "",
        skills: resumeData.skills || [],
        interests: resumeData.interests || [],
        experience_summary: resumeData.experience_summary || "",
        position: resumeData.position || "",
        job_id: resumeData.job_id || null,
        resume_id: resumeData.resume_id || null,
        resume_url: resumeData.resume_url || null,
      };

      await submitCandidateDetails(payload);
      // alert("Application submitted successfully!");
      setNotification({ message: "Application submitted successfully!", type: "is-success" });
    } catch (error) {
      console.error("Error submitting application:", error);
      // alert("Failed to submit application.");
      setNotification({ message: "Failed to submit application.", type: "is-danger" });
    }
  };

  // const selectedJob = jobs.find((job) => job.title === resumeData.position);
  const selectedJob = jobs.find((job) => job.id === resumeData.job_id);



  /* -------------------------------------------------------------------------- */
  /*                                    JSX                                     */
  /* -------------------------------------------------------------------------- */
  return (
    <div className="resume-container">
      {/* Notification */}
      {notification.message && (
        <div className={`notification ${notification.type}`}>
          <button
            className="delete"
            onClick={() => setNotification({ message: "", type: "" })}
          ></button>
          {notification.message}
        </div>
      )}

      <div className="resume-grid">
        {/* Left Side: Upload & Preview */}
        <div
          className="upload-box"
          onDrop={handleFileDrop}
          onDragOver={(e) => e.preventDefault()}
        >
          {!file ? (
            <div>
              {/* Upload Icon */}
              <div style={{ fontSize: "2.5rem", color: "#6366f1", marginBottom: "1rem" }}>
                📄
              </div>

              <p className="upload-text">Drag & Drop resume here</p>

              {/* Hidden File Input */}
              <input
                id="fileInput"
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={handleFileChange}
                style={{ display: "none" }}
              />

              {/* Choose File Button */}
              <label htmlFor="fileInput" className="btn-secondary" style={{ cursor: "pointer" }}>
                Choose File
              </label>
            </div>
          ) : (
            <div className="file-preview">
              <p>📄 {file.name}</p>

              {/* File Preview link */}
              {filePreviewUrl && (
                <a
                  href={filePreviewUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-secondary"
                >
                  Preview File
                </a>
              )}

              {/* Upload & Autofill Button */}
              <button
                onClick={handleUpload}
                disabled={loading}
                className="btn-primary"
                style={{ marginTop: "1rem", width: "100%" }}
              >
                {loading ? "Parsing..." : "Upload & Autofill"}
              </button>
            </div>
          )}
        </div>




        {/* Right Side: Form */}
        <form className="form-box" onSubmit={handleSubmit}>
          <h2 className="form-title">Application Details</h2>

          {/* Position */}
          <div className="form-group">
            <label>Position Applying For</label>
            {/* <select
              name="position"
              value={resumeData.position}
              onChange={handleChange}
            >
              <option value="">Select Position</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.title}>
                  {job.title}
                </option>
              ))}
            </select> */}
            <select
              name="job_id"
              value={resumeData.job_id}
              onChange={(e) => {
                const selectedId = e.target.value;
                const selectedJob = jobs.find((job) => job.id === selectedId);

                setResumeData((prev) => ({
                  ...prev,
                  job_id: selectedId,
                  position: selectedJob ? selectedJob.title : ""
                }));
              }}
            >
              <option value="">Select Position</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title}
                </option>
              ))}
            </select>

          </div>

          {/* Toggle Button */}
          {resumeData.position && (
            <button
              type="button"
              className="toggle-btn"
              onClick={() => setShowDetails((prev) => !prev)}
            >
              {showDetails ? "Hide Details ▲" : "Show Details ▼"}
            </button>
          )}

          {/* Job Details with animation */}
          <div className={`job-details ${showDetails ? "open" : ""}`}>
            {selectedJob && (
              <div>
                <h3>{selectedJob.title}</h3>
                <p><strong>Department:</strong> {selectedJob.department}</p>
                <p><strong>Location:</strong> {selectedJob.location}</p>
                <p><strong>Work Mode:</strong> {selectedJob.workMode}</p>
                <p><strong>Type:</strong> {selectedJob.type}</p>
                <p><strong>Experience:</strong> {selectedJob.experience}</p>
                <p><strong>Openings:</strong> {selectedJob.openings}</p>
                <p><strong>Salary:</strong> {selectedJob.salary}</p>

                {/* Render rich text safely */}
                <div className="job-section">
                  <h4>Description</h4>
                  <div dangerouslySetInnerHTML={{ __html: selectedJob.description }} />
                </div>

                <div className="job-section">
                  <h4>Responsibilities</h4>
                  <div dangerouslySetInnerHTML={{ __html: selectedJob.responsibilities }} />
                </div>

                <div className="job-section">
                  <h4>Requirements</h4>
                  <div dangerouslySetInnerHTML={{ __html: selectedJob.requirements }} />
                </div>

                <div className="job-section">
                  <h4>Benefits</h4>
                  <div dangerouslySetInnerHTML={{ __html: selectedJob.benefits }} />
                </div>
              </div>
            )}
          </div>


          {/* Name */}
          <div className="form-group">
            <label>Full Name</label>
            <input
              type="text"
              name="name"
              value={resumeData.name || ""}
              onChange={handleChange}
            />
          </div>

          {/* Email */}
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={resumeData.email || ""}
              onChange={handleChange}
            />
          </div>

          {/* Phone */}
          <div className="form-group">
            <label>Phone</label>
            <input
              type="text"
              name="phone"
              value={resumeData.phone || ""}
              onChange={handleChange}
            />
          </div>

          {/* Location */}
          <div className="form-group">
            <label>Location</label>
            <input
              type="text"
              name="location"
              value={resumeData.location || ""}
              onChange={handleChange}
            />
          </div>

          {/* Years of Experience */}
          <div className="form-group">
            <label>Years of Experience</label>
            <input
              type="number"
              name="years_of_experience"
              value={resumeData.years_of_experience || ""}
              onChange={handleChange}
            />
          </div>

          {/* Skills (Tag Input) */}
          <div className="form-group">
            <label>Skills</label>
            <div className="tag-input">
              {resumeData.skills.map((skill, i) => (
                <span key={i} className="tag">
                  {skill}
                  <button
                    type="button"
                    onClick={() => removeTag("skills", i)}
                  >
                    ×
                  </button>
                </span>
              ))}
              <input
                type="text"
                placeholder="Add a skill & press Enter"
                onKeyDown={(e) => handleTagInput(e, "skills")}
              />
            </div>
          </div>

          {/* Interests (Tag Input) */}
          <div className="form-group">
            <label>Interests</label>
            <div className="tag-input">
              {resumeData.interests.map((interest, i) => (
                <span key={i} className="tag">
                  {interest}
                  <button
                    type="button"
                    onClick={() => removeTag("interests", i)}
                  >
                    ×
                  </button>
                </span>
              ))}
              <input
                type="text"
                placeholder="Add interest & press Enter"
                onKeyDown={(e) => handleTagInput(e, "interests")}
              />
            </div>
          </div>

          {/* Summary */}
          <div className="form-group">
            <label>Professional Summary</label>
            <textarea
              name="experience_summary"
              value={resumeData.experience_summary || ""}
              onChange={handleChange}
            ></textarea>
          </div>

          {/* Submit */}
          <button type="submit" className="btn-success">
            Submit Application
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResumeUpload;
