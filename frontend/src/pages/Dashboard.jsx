// src/pages/Dashboard.jsx
import ResumeUpload from "../components/ResumeUpload";

export default function Dashboard() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">HR Dashboard</h1>
      <ResumeUpload />
    </div>
  );
}
