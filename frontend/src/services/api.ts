import axios from "axios";
import type { AxiosResponse } from "axios";

// Base Axios instance
const api = axios.create({
  baseURL: "/api",
});

// const api = axios.create({
//   baseURL: "http://localhost:8000/api",
// });

/* -------------------------------------------------------------------------- */
/*                                Candidate APIs                              */
/* -------------------------------------------------------------------------- */

export const uploadResume = async (
  file: File
): Promise<AxiosResponse<any>> => {
  const formData = new FormData();
  formData.append("file", file); // must match backend field name
  return api.post("/resume/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

// export const submitCandidateDetails = async (
//   data: Record<string, any>
// ): Promise<AxiosResponse<any>> => {
//   return api.post("/candidates", data, {
//     headers: { "Content-Type": "application/json" },
//   });
// };

// services/api.ts
export const submitCandidateDetails = async (data: Record<string, any>) => {
  return api.post("/candidates/", data, {
    headers: { "Content-Type": "application/json" },
  });
};






export const fetchAllCandidates = async (): Promise<AxiosResponse<any>> => {
  return api.get("/candidates");
};

export const fetchCandidateById = async (
  id: string
): Promise<AxiosResponse<any>> => {
  return api.get(`/candidates/${id}`);
};

export const updateCandidate = async (
  id: string,
  data: Record<string, any>
): Promise<AxiosResponse<any>> => {
  return api.put(`/candidates/${id}`, data, {
    headers: { "Content-Type": "application/json" },
  });
};

export const deleteCandidate = async (
  id: string
): Promise<AxiosResponse<any>> => {
  return api.delete(`/candidates/${id}`);
};

export const inactivateCandidate = async (
  id: string
): Promise<AxiosResponse<any>> => {
  return api.patch(`/candidates/${id}/inactivate`);
};

/* -------------------------------------------------------------------------- */
/*                                   Jobs APIs                                */
/* -------------------------------------------------------------------------- */

export const fetchJobPositions = async (): Promise<AxiosResponse<any>> => {
  return api.get("/jobs/positions");
};

/* -------------------------------------------------------------------------- */
/*                 Generate job details with AI                               */
/* -------------------------------------------------------------------------- */
export const generateJobDetails = async (title: string) => {
  return api.post("/ai/jobs/generate", { title }, {
    headers: { "Content-Type": "application/json" },
  });
};


export default api;
