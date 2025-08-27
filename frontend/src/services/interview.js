// src/services/interview.js
import API from "./api";

export const startInterview = async (candidateId) => {
  const res = await API.post(`/interview/start`, { candidateId });
  return res.data;
};

export const askQuestion = async (candidateId, answer) => {
  const res = await API.post(`/interview/ask`, { candidateId, answer });
  return res.data;
};
