// src/components/ResumeUpload.jsx
import { useState } from "react";
import { uploadResume } from "../services/resume";

export default function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    try {
      const data = await uploadResume(file);
      setResult(data);
    } catch (err) {
      console.error("Resume upload failed", err);
    }
  };

  return (
    <div className="p-6 border rounded-2xl shadow-md bg-white">
      <h2 className="text-xl font-semibold mb-4">Upload Resume</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={(e) => setFile(e.target.files[0])}
          className="mb-3"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Upload
        </button>
      </form>

      {result && (
        <div className="mt-4 p-3 border rounded bg-gray-50">
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
