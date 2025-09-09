import { Routes, Route } from "react-router-dom";
import Navbar from "./components/common/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ResumeUploadPage from  "./pages/ResumeUpload"
import JobOpenings from "./pages/JobOpenings";
import JobOpeningsList from "./pages/JobOpeningsList";
import ThankYouPage from "./pages/ThankYouPage";

function App() {
  return (
    <>
      <Navbar />
      <div className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/resume-upload" element={<ResumeUploadPage />} />
          <Route path="/create-job-openings" element={<JobOpenings />} />
          <Route path="/view-job-openings" element={<JobOpeningsList />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/thank-you" element={<ThankYouPage />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
