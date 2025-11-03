import React, { useState, useRef, useEffect } from "react";
import "./css/BulkResumeUpload.css";
import api, { fetchAllJobs, generateCandidateScore } from "../services/api";
import Swal from "sweetalert2";

interface UploadFile {
  file: File;
  progress: number;
  status: "pending" | "uploading" | "done" | "error" | "cancelled";
  speed?: number;
  eta?: string;
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
  status: number;
}

const MAX_FILES = 15;

const BulkResumeUpload: React.FC = () => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<{ job_id: string; position: string }>({
    job_id: "",
    position: "",
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  /** ------------------------
   * Fetch active jobs for dropdown
   ------------------------ **/
  useEffect(() => {
    const loadJobs = async () => {
      try {
        const response = await fetchAllJobs();
        const activeJobs = (response.data || []).filter((job: Job) => job.status === 1);
        setJobs(activeJobs);
      } catch (error) {
        console.error("Failed to fetch jobs:", error);
      }
    };
    loadJobs();
  }, []);

  /** ------------------------
   * Add new files with limit
   ------------------------ **/
  const addFiles = (fileList: File[]) => {
    const remainingSlots = MAX_FILES - files.length;
    if (remainingSlots <= 0) {
      Swal.fire("Limit Reached", `You can upload up to ${MAX_FILES} files only.`, "warning");
      return;
    }

    const filesToAdd = fileList.slice(0, remainingSlots);
    const newFiles = filesToAdd.map((file) => ({
      file,
      progress: 0,
      status: "pending" as const,
    }));

    setFiles((prev) => [...prev, ...newFiles]);

    if (fileList.length > remainingSlots) {
      Swal.fire(
        "Limit Warning",
        `Only ${remainingSlots} files were added. Maximum ${MAX_FILES} allowed.`,
        "info"
      );
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    addFiles(Array.from(e.dataTransfer.files));
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => e.preventDefault();

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) addFiles(Array.from(e.target.files));
  };

  /** ------------------------
   * Single bulk upload API
   ------------------------ **/
  const uploadBulkResumes = async (
    files: File[],
    job_id: string,
    position: string,
    onProgress?: (percent: number) => void
  ) => {
    const formData = new FormData();
    files.forEach((file) => formData.append("files[]", file)); // 👈 important name
    formData.append("job_id", job_id);
    formData.append("position", position);

    return api.post("/resume/bulk-upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (event) => {
        if (event.total) {
          const percent = Math.round((event.loaded * 100) / event.total);
          if (onProgress) onProgress(percent);
        }
      },
    });
  };

  /** ------------------------
   * Handle Start Upload
   ------------------------ **/
  const handleStartUpload = async () => {
    // Validation 1: No files selected
    if (files.length === 0) {
      Swal.fire({
        title: "No Files Selected",
        text: "Please upload at least one resume before starting the upload.",
        icon: "warning",
        confirmButtonText: "OK",
      });
      return;
    }

    // Validation 2: Job not selected
    if (!selectedJob.job_id || !selectedJob.position) {
      Swal.fire({
        title: "Job Not Selected",
        text: "Please select a job position before uploading resumes.",
        icon: "warning",
        confirmButtonText: "OK",
      });
      return;
    }

    // Proceed to confirmation
    const result = await Swal.fire({
      title: "Start Upload?",
      text: `You’re about to upload ${files.length} file(s) for position: ${selectedJob.position}`,
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Yes, upload",
      cancelButtonText: "Cancel",
    });

    if (!result.isConfirmed) return;

    // Continue with upload logic
    setUploading(true);
    setOverallProgress(0);
    setFiles((prev) => prev.map((f) => ({ ...f, status: "uploading", progress: 0 })));

    try {
      const startTime = Date.now();

      const response = await uploadBulkResumes(
        files.map((f) => f.file),
        selectedJob.job_id,
        selectedJob.position,
        (percent) => {
          const elapsed = (Date.now() - startTime) / 1000;
          const uploadedBytes = (percent / 100) * (files.reduce((acc, f) => acc + f.file.size, 0));
          const speed = uploadedBytes / elapsed / 1024; // KB/s
          const remaining = (100 - percent) * (elapsed / percent);
          const eta = `${Math.round(remaining)}s`;

          setOverallProgress(percent);
          setFiles((prev) =>
            prev.map((f) => ({
              ...f,
              progress: percent,
              speed: Math.round(speed),
              eta,
            }))
          );
        }
      );

      console.log("Bulk upload success:", response.data);

      const results = response.data?.results || [];
      if (results.length === 0) {
        Swal.fire("No Candidates", "No candidates were returned from upload.", "warning");
        return;
      }

      // Step 1: Show processing loader
      Swal.fire({
        title: "Processing Candidates...",
        html: `<b>0</b> / ${results.length} candidates scored.`,
        allowOutsideClick: false,
        didOpen: () => Swal.showLoading(),
      });

      // Step 2: Sequential or parallel score generation
      let completed = 0;

      for (const candidate of results) {
        try {
          await generateCandidateScore(candidate.candidate_id);
          completed++;
          Swal.update({
            html: `<b>${completed}</b> / ${results.length} candidates scored.`,
          });
          console.log(`🎯 Score generated for candidate ID: ${candidate.candidate_id}`);
        } catch (err) {
          console.error(`❌ Failed to generate score for candidate ID ${candidate.candidate_id}:`, err);
        }
      }

      // Step 3: Done state
      Swal.close();
      setFiles((prev) =>
        prev.map((f) => ({
          ...f,
          progress: 100,
          status: "done",
          eta: "Completed",
        }))
      );
      setOverallProgress(100);

      Swal.fire("Success!", "All resumes processed and scores generated successfully!", "success");
      setFiles([]);
    } catch (error) {
      console.error("❌ Upload failed:", error);
      Swal.fire("Error", "Upload failed. Please try again.", "error");
      setFiles((prev) => prev.map((f) => ({ ...f, status: "error" })));
    } finally {
      setUploading(false);
    }
  };


  /** ------------------------
   * Cancel Upload
   ------------------------ **/
  const handleCancelAll = async () => {
    const result = await Swal.fire({
      title: "Cancel Upload?",
      text: "Are you sure you want to cancel all uploads?",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, cancel",
      cancelButtonText: "No",
    });

    if (!result.isConfirmed) return;

    setFiles([]);
    setOverallProgress(0);
    Swal.fire("Cancelled", "All uploads have been cancelled.", "info");
  };

  return (
    <section className="bulk-upload-container">
      <h2>Bulk Resume Upload</h2>

      {/* ------------------ Job Selection ------------------ */}
      <div className="form-group job-dropdown">
        <label>Select Job Position</label>
        <select
          value={selectedJob.job_id}
          onChange={(e) => {
            const id = e.target.value;
            const job = jobs.find((j) => j.id === id);
            setSelectedJob({
              job_id: id,
              position: job ? job.title : "",
            });
          }}
          disabled={uploading}
        >
          <option value="">Select Position</option>
          {jobs.map((job) => (
            <option key={job.id} value={job.id}>
              {job.title}
            </option>
          ))}
        </select>
      </div>

      {/* ------------------ Upload Section ------------------ */}
      {files.length === 0 ? (
        <div
          className="drop-zone centered-drop-zone"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={() => fileInputRef.current?.click()}
        >
          <p>
            Drag & drop resumes here or <span>click to browse</span>
          </p>
          <input type="file" multiple ref={fileInputRef} onChange={handleFileSelect} />
        </div>
      ) : (
        <div className="bulk-upload-grid">
          <div
            className="drop-zone left-drop-zone"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => fileInputRef.current?.click()}
          >
            <p>
              Add more resumes or <span>click to browse</span>
            </p>
            <input type="file" multiple ref={fileInputRef} onChange={handleFileSelect} />
          </div>

          <div className="upload-progress-side">
            <div className="file-list-scroll">
              {files.map((file, index) => (
                <div className="file-item" key={index}>
                  <div className="file-details">
                    <div className="file-name" title={file.file.name}>
                      {file.file.name.length > 40
                        ? file.file.name.slice(0, 40) + "..."
                        : file.file.name}
                    </div>
                    <div className="file-meta">
                      {file.progress}% • {file.speed ? `${file.speed} KB/s` : "--"} •{" "}
                      {file.eta || "--"}
                    </div>
                    <div className="progress-bar">
                      <div
                        className={`progress-inner ${file.status === "done"
                            ? "progress-green"
                            : file.status === "error"
                              ? "progress-red"
                              : "progress-blue"
                          }`}
                        style={{ width: `${file.progress}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="overall-progress">
              <div className="overall-progress-bar">
                <div
                  className="overall-progress-inner"
                  style={{ width: `${overallProgress}%` }}
                />
              </div>
              <p>Overall Progress: {overallProgress}%</p>
            </div>

            <div className="upload-actions-fixed">
              <button
                className="start-upload-btn"
                onClick={handleStartUpload}
                disabled={uploading}
              >
                {uploading ? "Processing..." : "Start Upload"}
              </button>
              <button
                className="cancel-upload-btn"
                onClick={handleCancelAll}
                disabled={uploading}
              >
                Cancel All
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default BulkResumeUpload;
