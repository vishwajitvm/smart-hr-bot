// src/services/resume.js
import API from "./api";

export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await API.post("/resume/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};
