import axios from "axios";
import type { AxiosResponse } from "axios";

// ✅ Base Axios instance
const api = axios.create({
  baseURL: "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

/* -------------------------------------------------------------------------- */
/*                                API METHODS                                 */
/* -------------------------------------------------------------------------- */

/**
 * Upload a resume file (PDF, DOCX, etc.)
 */
export const uploadResume = async (
  file: File
): Promise<AxiosResponse<any>> => {
  const formData = new FormData();
  formData.append("resume", file);

  return api.post("/resume/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

/**
 * Submit candidate details (autofilled + user edited form)
 */
export const submitCandidateDetails = async (
  data: Record<string, any>
): Promise<AxiosResponse<any>> => {
  return api.post("/resume/submit", data);
};

/**
 * Fetch available job positions
 */
export const fetchJobPositions = async (): Promise<AxiosResponse<any>> => {
  return api.get("/jobs/positions");
};

/* -------------------------------------------------------------------------- */

export default api;
