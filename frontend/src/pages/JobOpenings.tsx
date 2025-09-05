import { useState } from "react";
import ReactQuill from "react-quill-new";
import "react-quill-new/dist/quill.snow.css";
import "./css/JobOpenings.css";
import { createJob, generateJobDetails } from "../services/api";

export default function JobOpenings() {
const [job, setJob] = useState({
    title: "",
    department: "",
    location: "",
    workMode: "On-site",
    type: "Full-time",
    experience: "Entry",
    openings: 1,
    salary: "",
    deadline: "",
    description: "",
    responsibilities: "",
    requirements: "",
    benefits: "",
    status: 2,
    hiringManager: "",
    visibility: "Public",
    applicationMethod: "Direct Apply",
    model: "",
    duration_ms: "",
    cached: "",
    token: "",
  });

  const [loadingAI, setLoadingAI] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    setJob((prev) => ({
      ...prev,
      [name]: type === "number" ? Number(value) : value,
    }));
  };

  const handleQuillChange = (field: string, value: string) => {
    setJob((prev) => ({ ...prev, [field]: value }));
  };

  // Save to backend
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setSaving(true);

      const payload = {
        ...job,
        deadline: job.deadline ? new Date(job.deadline).toISOString() : null,
        model: job.model || null,
        duration_ms: job.duration_ms || null,
        cached: job.cached ?? null,
        token: job.token || null,
      };

      const res = await createJob(payload);
      console.log("Job saved:", res.data);

      alert("Job saved successfully!");
      setJob({
        title: "",
        department: "",
        location: "",
        workMode: "On-site",
        type: "Full-time",
        experience: "Entry",
        openings: 1,
        salary: "",
        deadline: "",
        description: "",
        responsibilities: "",
        requirements: "",
        benefits: "",
        status: 2,
        hiringManager: "",
        visibility: "Public",
        applicationMethod: "Direct Apply",
        model: "",
        duration_ms: "",
        cached: "",
        token: "",
      });
    } catch (err) {
      console.error("Failed to save job:", err);
      alert("Failed to save job. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const normalizeExperience = (exp: string): string => {
    if (!exp) return "Entry";
    const lower = exp.toLowerCase();
    if (lower.includes("entry")) return "Entry";
    if (lower.includes("junior")) return "Entry";
    if (lower.includes("mid")) return "Mid";
    if (lower.includes("senior") || lower.includes("lead")) return "Senior";
    return "Mid"; // fallback
  };

  const normalizeWorkMode = (mode: string): string => {
    if (!mode) return "On-site";
    const lower = mode.toLowerCase();
    if (lower.includes("remote")) return "Remote";
    if (lower.includes("hybrid")) return "Hybrid";
    return "On-site";
  };

  // AI auto-fill
  const handleAIClick = async () => {
    if (!job.title) {
      alert("Please enter a Job Title first!");
      return;
    }

    try {
      setLoadingAI(true);
      const res = await generateJobDetails(job.title);
      const ai = res.data.generated || {};

      setJob((prev) => ({
        ...prev,
        title: ai.title || prev.title,
        department: ai.department || prev.department,
        location: ai.location || prev.location,
        workMode: normalizeWorkMode(ai.workMode) || prev.workMode,
        type: ai.type || prev.type,
        experience: normalizeExperience(ai.experience) || prev.experience,
        openings: ai.openings ?? prev.openings,
        salary: ai.salary || prev.salary,
        description: ai.description || prev.description,
        responsibilities: ai.responsibilities || prev.responsibilities,
        requirements: ai.requirements || prev.requirements,
        benefits: ai.benefits || prev.benefits,
        hiringManager: ai.hiringManager || prev.hiringManager,
        // leave these as user inputs
        deadline: prev.deadline,
        status: prev.status,
        visibility: prev.visibility,
        applicationMethod: prev.applicationMethod,
        model: res.data.model,
        duration_ms: res.data.duration_ms,
        cached: res.data.cached,
        token: res.data.token,
      }));
    } catch (err) {
      console.error("AI generation failed:", err);
      alert("Failed to generate job details. Please try again.");
    } finally {
      setLoadingAI(false);
    }
  };

  // Rich text toolbar config
  const quillModules = {
    toolbar: [
      [{ header: [1, 2, 3, false] }],
      ["bold", "italic", "underline", "strike"],
      [{ list: "ordered" }, { list: "bullet" }],
      [{ align: [] }],
      ["link"],
      ["clean"],
    ],
  };

  return (
    <div className="job-page">
      <div className="job-card">
        <h1 className="job-title">Create Job Opening</h1>

        <form onSubmit={handleSubmit} className="job-form">
          {/* Job Title with AI Button */}
          <div className="field">
            <label className="label">Job Title</label>
            <div className="control has-icons-right" style={{ position: "relative" }}>
              <input
                type="text"
                name="title"
                value={job.title}
                onChange={handleChange}
                placeholder="e.g. Software Engineer"
                required
                className="input"
              />
              <button
                type="button"
                className="ai-button"
                onClick={handleAIClick}
                disabled={loadingAI}
              >
                {loadingAI ? "Generating..." : "✨ Write with AI"}
              </button>
            </div>
          </div>

          {/* Department + Hiring Manager */}
          <div className="columns">
            <div className="column">
              <label className="label">Department / Team</label>
              <input
                type="text"
                name="department"
                value={job.department}
                onChange={handleChange}
                placeholder="e.g. Engineering, Marketing"
                className="input"
              />
            </div>
            <div className="column">
              <label className="label">Hiring Manager</label>
              <input
                type="text"
                name="hiringManager"
                value={job.hiringManager}
                onChange={handleChange}
                placeholder="e.g. John Doe"
                className="input"
              />
            </div>
          </div>

          {/* Location + Work Mode */}
          <div className="columns">
            <div className="column">
              <label className="label">Location</label>
              <input
                type="text"
                name="location"
                value={job.location}
                onChange={handleChange}
                placeholder="e.g. New York, Remote"
                className="input"
              />
            </div>
            <div className="column">
              <label className="label">Work Mode</label>
              <div className="select is-fullwidth">
                <select
                  name="workMode"
                  value={job.workMode}
                  onChange={handleChange}
                >
                  <option>On-site</option>
                  <option>Remote</option>
                  <option>Hybrid</option>
                </select>
              </div>
            </div>
          </div>

          {/* Employment Type + Experience */}
          <div className="columns">
            <div className="column">
              <label className="label">Employment Type</label>
              <div className="select is-fullwidth">
                <select name="type" value={job.type} onChange={handleChange}>
                  <option>Full-time</option>
                  <option>Part-time</option>
                  <option>Internship</option>
                  <option>Contract</option>
                </select>
              </div>
            </div>
            <div className="column">
              <label className="label">Experience Level</label>
              <div className="select is-fullwidth">
                <select
                  name="experience"
                  value={job.experience}
                  onChange={handleChange}
                >
                  <option>Entry</option>
                  <option>Mid</option>
                  <option>Senior</option>
                </select>
              </div>
            </div>
          </div>

          {/* Openings */}
          <div className="field">
            <label className="label">No. of Openings</label>
            <input
              type="number"
              name="openings"
              value={job.openings}
              onChange={handleChange}
              min={1}
              className="input"
            />
          </div>

          {/* Salary + Deadline */}
          <div className="columns">
            <div className="column">
              <label className="label">Salary Range</label>
              <input
                type="text"
                name="salary"
                value={job.salary}
                onChange={handleChange}
                placeholder="e.g. $60k - $80k / year"
                className="input"
              />
            </div>
            <div className="column">
              <label className="label">Application Deadline</label>
              <input
                type="date"
                name="deadline"
                value={job.deadline}
                onChange={handleChange}
                className="input"
              />
            </div>
          </div>

          {/* Rich Text Fields */}
          {[
            { label: "Job Description", field: "description" },
            { label: "Responsibilities", field: "responsibilities" },
            { label: "Requirements", field: "requirements" },
            { label: "Benefits / Perks", field: "benefits" },
          ].map(({ label, field }) => (
            <div className="field" key={field}>
              <label className="label">{label}</label>
              <ReactQuill
                theme="snow"
                value={job[field as keyof typeof job] as string}
                onChange={(val) => handleQuillChange(field, val)}
                modules={quillModules}
              />
            </div>
          ))}

          {/* Status */}
          <div className="field">
            <label className="label">Status</label>
            <div className="select is-fullwidth">
              <select name="status" value={job.status} onChange={handleChange}>
                <option value={0}>Inactive</option>
                <option value={1}>Active (Published)</option>
                <option value={2}>Draft</option>
              </select>
            </div>
          </div>

          {/* Visibility */}
          <div className="field">
            <label className="label">Visibility</label>
            <div className="select is-fullwidth">
              <select
                name="visibility"
                value={job.visibility}
                onChange={handleChange}
              >
                <option>Public</option>
                <option>Internal Only</option>
              </select>
            </div>
          </div>

          {/* Application Method */}
          <div className="field">
            <label className="label">Application Method</label>
            <div className="select is-fullwidth">
              <select
                name="applicationMethod"
                value={job.applicationMethod}
                onChange={handleChange}
              >
                <option>Direct Apply</option>
                <option>External Link</option>
              </select>
            </div>
          </div>

          {/* Buttons */}
          <div className="form-actions">
            {/* <button
              type="button"
              className="button is-light"
              onClick={() => alert("Preview Coming Soon")}
            >
              Preview
            </button> */}
            <button type="submit" className="button is-primary">
              Save Job
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
