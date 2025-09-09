import { useEffect, useState, useRef } from "react";
import Swal from "sweetalert2";
import { useNavigate } from "react-router-dom";
import {
  fetchAllJobs,
  deleteJob,
  updateJob,
  fetchJobById,
} from "../services/api";
import "bulma/css/bulma.min.css";
import "./css/JobOpeningsList.css";

interface Job {
  id: string;
  title: string;
  department?: string;
  location?: string;
  workMode?: string;
  type?: string;
  experience?: string;
  openings?: number;
  salary?: string;
  deadline?: string | null;
  description?: string;
  responsibilities?: string;
  requirements?: string;
  benefits?: string;
  status?: number;
  hiringManager?: string;
  visibility?: string;
  applicationMethod?: string;
  created_at?: string;
  updated_at?: string;
}

export default function JobOpeningsList() {
  const hasFetched = useRef(false);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [filteredJobs, setFilteredJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const jobsPerPage = 5;
  const [notification, setNotification] = useState<{
      message: string;
      type: "is-success" | "is-danger" | "is-warning" | "is-info" | "" ;
    }>({ message: "", type: "" });

  const navigate = useNavigate();

  useEffect(() => {
    if (!hasFetched.current) {
      fetchJobs();
      hasFetched.current = true;
    }
  }, []);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const res = await fetchAllJobs();
      setJobs(res.data);
      setFilteredJobs(res.data);
    } catch (err) {
      console.error("Failed to fetch jobs", err);
      setNotification({ message: "Unable to fetch jobs", type: "is-danger" });
    } finally {
      setLoading(false);
    }
  };

  // Search jobs
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value.toLowerCase();
    setSearchTerm(term);
    const results = jobs.filter(
      (job) =>
        job.title.toLowerCase().includes(term) ||
        job.department?.toLowerCase().includes(term) ||
        job.location?.toLowerCase().includes(term)
    );
    setFilteredJobs(results);
    setCurrentPage(1);
  };

  // Delete Job
  const handleDelete = async (id: string) => {
    const result = await Swal.fire({
      title: "Are you sure?",
      text: "This job will be deleted permanently.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, delete it!",
      cancelButtonText: "Cancel",
    });

    if (result.isConfirmed) {
      try {
        await deleteJob(id);
        setNotification({ message: "Job deleted successfully!", type: "is-success" });
        fetchJobs();
      } catch (err) {
        setNotification({ message: "Failed to delete job.", type: "is-danger" });
      }
    }
  };

  // Toggle status
  const handleStatusToggle = async (job: Job) => {
    const newStatus = job.status === 1 ? 0 : 1;
    try {
      await updateJob(job.id, { status: newStatus });
      setJobs((prev) =>
        prev.map((j) => (j.id === job.id ? { ...j, status: newStatus } : j))
      );
      setFilteredJobs((prev) =>
        prev.map((j) => (j.id === job.id ? { ...j, status: newStatus } : j))
      );
      setNotification({
        message: `Status updated to ${newStatus === 1 ? "Active" : "Inactive"}`,
        type: "is-info",
      });
    } catch (err) {
      setNotification({ message: "Failed to update status.", type: "is-danger" });
    }
  };

  // Preview Job
  const handlePreview = async (id: string) => {
    try {
      const res = await fetchJobById(id);
      const job: Job = res.data;

      Swal.fire({
        title: `<h2 class="title is-4">${job.title}</h2>`,
        html: `
          <div class="card">
            <div class="card-content has-text-left">
              <p><strong>Department:</strong> ${job.department || "-"}</p>
              <p><strong>Location:</strong> ${job.location || "-"}</p>
              <p><strong>Work Mode:</strong> ${job.workMode || "-"}</p>
              <p><strong>Type:</strong> ${job.type || "-"}</p>
              <p><strong>Experience:</strong> ${job.experience || "-"}</p>
              <p><strong>Openings:</strong> ${job.openings || "-"}</p>
              <p><strong>Salary:</strong> ${job.salary || "-"}</p>
              <p><strong>Hiring Manager:</strong> ${job.hiringManager || "-"}</p>
              <p><strong>Visibility:</strong> ${job.visibility || "-"}</p>
              <p><strong>Application Method:</strong> ${job.applicationMethod || "-"}</p>
              <hr>
              <h3 class="subtitle is-5">Description</h3>
              <div class="content">${job.description || "N/A"}</div>
              <h3 class="subtitle is-5">Responsibilities</h3>
              <div class="content">${job.responsibilities || "N/A"}</div>
              <h3 class="subtitle is-5">Requirements</h3>
              <div class="content">${job.requirements || "N/A"}</div>
              <h3 class="subtitle is-5">Benefits</h3>
              <div class="content">${job.benefits || "N/A"}</div>
            </div>
          </div>
        `,
        width: "800px",
        showCloseButton: true,
        confirmButtonText: "Close",
        customClass: {
          popup: "job-preview-popup",
        },
      });
    } catch (err) {
      setNotification({ message: "Failed to fetch job details.", type: "is-danger" });
    }
  };

  // Pagination
  const indexOfLastJob = currentPage * jobsPerPage;
  const indexOfFirstJob = indexOfLastJob - jobsPerPage;
  const currentJobs = filteredJobs.slice(indexOfFirstJob, indexOfLastJob);
  const totalPages = Math.ceil(filteredJobs.length / jobsPerPage);

  return (
    <div className="container mt-5">
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

      <div className="level mb-4">
        <div className="level-left">
          <h1 className="title has-text-dark">Job Openings</h1>
        </div>

        <div className="level-right">
          <div className="field has-addons mr-3">
            <div className="control">
              <input
                type="text"
                className="input"
                placeholder="Search by title, department, location..."
                value={searchTerm}
                onChange={handleSearch}
              />
            </div>
          </div>
          <div className="control">
            <button
              className="button is-primary"
              onClick={
                () => navigate("/create-job-openings")
              }
            >
              + Add Job
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="table-container">
          <table className="table is-striped is-hoverable is-fullwidth custom-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Department</th>
                <th>Location</th>
                <th>Type</th>
                <th>Experience</th>
                <th>Openings</th>
                <th>Status</th>
                <th>Salary</th>
                <th className="has-text-centered">Actions</th>
              </tr>
            </thead>
            <tbody>
              {currentJobs.length > 0 ? (
                currentJobs.map((job) => (
                  <tr key={job.id}>
                    <td>{job.title}</td>
                    <td>{job.department || "-"}</td>
                    <td>{job.location || "-"}</td>
                    <td>{job.type}</td>
                    <td>{job.experience}</td>
                    <td>{job.openings}</td>
                    <td>
                      <label className="switch">
                        <input
                          type="checkbox"
                          checked={job.status === 1}
                          onChange={() => handleStatusToggle(job)}
                        />
                        <span className="check"></span>
                      </label>
                    </td>
                    <td>{job.salary || "-"}</td>
                    <td className="has-text-centered">
                      <button
                        className="button is-small is-info mr-2"
                        onClick={() => handlePreview(job.id)}
                      >
                        Preview
                      </button>
                      <button
                        className="button is-small is-warning mr-2"
                        onClick={() =>
                          Swal.fire("Edit Job", job.title, "info")
                        }
                      >
                        Edit
                      </button>
                      <button
                        className="button is-small is-danger"
                        onClick={() => handleDelete(job.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="has-text-centered">
                    No jobs found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <nav
          className="pagination is-centered"
          role="navigation"
          aria-label="pagination"
        >
          <button
            className="pagination-previous"
            disabled={currentPage === 1}
            onClick={() => setCurrentPage((prev) => prev - 1)}
          >
            Previous
          </button>
          <button
            className="pagination-next"
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage((prev) => prev + 1)}
          >
            Next
          </button>
          <ul className="pagination-list">
            {Array.from({ length: totalPages }, (_, i) => (
              <li key={i}>
                <button
                  className={`pagination-link ${
                    currentPage === i + 1 ? "is-current" : ""
                  }`}
                  onClick={() => setCurrentPage(i + 1)}
                >
                  {i + 1}
                </button>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </div>
  );
}
