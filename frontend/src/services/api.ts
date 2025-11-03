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
  return api.get("/candidates/");
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
  return api.patch(`/candidates/${id}/inactivate/`);
};

/* -------------------------------------------------------------------------- */
/*                                   Jobs APIs                                */
/* -------------------------------------------------------------------------- */

// Fetch all jobs
export const fetchAllJobs = async (): Promise<AxiosResponse<any>> => {
  return api.get("/jobs/");
};

// Fetch job by ID
export const fetchJobById = async (
  id: string
): Promise<AxiosResponse<any>> => {
  return api.get(`/jobs/${id}`);
};

// Create a new job
export const createJob = async (
  data: Record<string, any>
): Promise<AxiosResponse<any>> => {
  return api.post("/jobs/", data, {
    headers: { "Content-Type": "application/json" },
  });
};

// Update job by ID
export const updateJob = async (
  id: string,
  data: Record<string, any>
): Promise<AxiosResponse<any>> => {
  return api.put(`/jobs/${id}`, data, {
    headers: { "Content-Type": "application/json" },
  });
};

// Soft delete job by ID
export const deleteJob = async (
  id: string
): Promise<AxiosResponse<any>> => {
  return api.delete(`/jobs/${id}`);
};

export const updateJobStatus = async (
  id: string,
  status: number
): Promise<AxiosResponse<any>> => {
  return api.patch(`/jobs/${id}/status`, { status }, {
    headers: { "Content-Type": "application/json" },
  });
};

/* -------------------------------------------------------------------------- */
/*                 Generate job details with AI                               */
/* -------------------------------------------------------------------------- */
export const generateJobDetails = async (title: string) => {
  return api.post("/ai/jobs/generate", { title }, {
    headers: { "Content-Type": "application/json" },
  });
};

/* -------------------------------------------------------------------------- */
/*                         Candidate Scoring APIs                              */
/* -------------------------------------------------------------------------- */
export const generateCandidateScore = async (
  candidateId: string
) => {
  return api.post("/candidate-scoring/generate-score", {
    candidate_id: candidateId,
  }, {
    headers: { "Content-Type": "application/json" },
  });
};

/* -------------------------------------------------------------------------- */
/*                   Candidate Listing With Score APIs                        */
/* -------------------------------------------------------------------------- */
// export const fetchCandidatesWithScores = (page = 1, limit = 10) =>
//   api.post("/candidates-listing-with-score/list", { page, limit });

// services/api.ts
export const fetchCandidatesWithScores = (
  page = 1,
  limit = 10,
  filters: any = {}
) => {
  return api.post("/candidates-listing-with-score/list", {
    page,
    limit,
    filters,
  });
};


export const fetchCandidateWithScoreById = (candidateId: string) =>
  api.post("/candidates-listing-with-score/get-candidate-by-id", {
    candidate_id: candidateId,
  });

/* -------------------------------------------------------------------------- */
/*                        Candidate Chat (AI Recruiter) API                   */
/* -------------------------------------------------------------------------- */
export async function candidateChat(candidateData: any, question: string) {
  return api.post("/candidates-listing-with-score/chat", {
    candidate: candidateData,
    question,
  });
}

/* -------------------------------------------------------------------------- */
/*                        Candidate Approval / Rejection APIs                 */
/* -------------------------------------------------------------------------- */

export const approveCandidate = async (candidateId: string) => {
  return api.post(`/candidates-listing-with-score/${candidateId}/approve`);
};

export const rejectCandidate = async (candidateId: string) => {
  return api.post(`/candidates-listing-with-score/${candidateId}/reject`);
};

/* -------------------------------------------------------------------------- */
/*            Approved Candidates Listing With Score API                      */
/* -------------------------------------------------------------------------- */
export const fetchApprovedCandidates = (
  page: number = 1,
  limit: number = 20
) => {
  return api.post("/candidates-listing-with-score/approved-candidates-list", {
    page,
    limit,
  });
};

/* -------------------------------------------------------------------------- */
/*                           Multi-file Bulk Upload                           */
/* -------------------------------------------------------------------------- */

export const uploadBulkResumes = async (files: File[], onProgress?: (percent: number) => void) => {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files[]", file);
  });

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


/* -------------------------------------------------------------------------- */
/*                      AI Voice Interview Initiation API                     */
/* -------------------------------------------------------------------------- */
export const initiateVoiceInterview = async (candidateData: Record<string, any>) => {
  return api.post("/ai/voice-interview/start", candidateData, {
    headers: { "Content-Type": "application/json" },
  });
};






export default api;
