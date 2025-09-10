import { useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  PieChart, Pie, Cell
} from "recharts";
import "./css/ResumeScoring.css";

export default function ResumeScoringDashboard() {
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("details");
  const [comparisonCandidates, setComparisonCandidates] = useState<any[]>([]);

  // Dummy candidate data
  const candidates = [
    { id: 1, name: "John Doe", email: "john@example.com", job: "Software Engineer", score: 78 },
    { id: 2, name: "Jane Smith", email: "jane@example.com", job: "Data Scientist", score: 85 },
  ];

  // Dummy scoring breakdown
  const scoreBreakdown = [
    { subject: "Skills", A: 75 },
    { subject: "Experience", A: 60 },
    { subject: "Education", A: 85 },
    { subject: "Projects", A: 70 },
    { subject: "Keywords", A: 80 },
    { subject: "ATS", A: 90 },
    { subject: "Grammar", A: 88 },
    { subject: "Soft Skills", A: 75 },
  ];

  const pieData = [
    { name: "Skills", value: 25 },
    { name: "Experience", value: 15 },
    { name: "Education", value: 20 },
    { name: "Projects", value: 15 },
    { name: "Keywords", value: 10 },
    { name: "ATS", value: 10 },
    { name: "Grammar", value: 5 },
  ];

  const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff8042", "#0088FE", "#FFBB28", "#FF8042"];

  // Advanced metrics placeholders
  const sentimentAnalysis = "Positive";
  const grammarScore = 90;
  const atsScore = 85;
  const skillMatchScore = 78;
  const readabilityScore = 80;

  return (
    <div className="resume-dashboard">
      {/* Left Filters */}
      <div className="filters">
        <h3>Filters</h3>
        <label>Date</label>
        <select>
          <option>This Week</option>
          <option>This Month</option>
          <option>Custom Range</option>
        </select>

        <label>Candidate Name</label>
        <input placeholder="Search by name" />

        <label>Job</label>
        <select>
          <option>All Jobs</option>
          <option>Software Engineer</option>
          <option>Data Scientist</option>
        </select>

        <label>Score Range</label>
        <input type="number" placeholder="Min Score" />
        <input type="number" placeholder="Max Score" />

        <label>Sentiment</label>
        <select>
          <option>All</option>
          <option>Positive</option>
          <option>Neutral</option>
          <option>Negative</option>
        </select>

        <button>Apply Filters</button>
      </div>

      {/* Right Panel */}
      <div className="results">
        <h2>Resume Scoring Results</h2>

        {/* Candidate Table */}
        <table className="candidate-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Job</th>
              <th>Score</th>
              <th>Action</th>
              <th>Compare</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map(c => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.email}</td>
                <td>{c.job}</td>
                <td>{c.score}%</td>
                <td>
                  <button onClick={() => setSelectedCandidate(c)}>View</button>
                </td>
                <td>
                  <input type="checkbox" onChange={(e) => {
                    if(e.target.checked) setComparisonCandidates([...comparisonCandidates, c]);
                    else setComparisonCandidates(comparisonCandidates.filter(cc => cc.id !== c.id));
                  }} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Selected Candidate Tabs */}
        {selectedCandidate && (
          <div className="candidate-details">
            <div className="tabs">
              <button className={activeTab === "details" ? "active" : ""} onClick={() => setActiveTab("details")}>Details & Scoring</button>
              <button className={activeTab === "chat" ? "active" : ""} onClick={() => setActiveTab("chat")}>AI Chat</button>
              <button className={activeTab === "comparison" ? "active" : ""} onClick={() => setActiveTab("comparison")}>Comparison</button>
            </div>

            {/* Details & Scoring */}
            {activeTab === "details" && (
              <div className="details-tab">
                <h3>{selectedCandidate.name}</h3>

                <div className="charts">
                  <RadarChart outerRadius={90} width={300} height={300} data={scoreBreakdown}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" />
                    <PolarRadiusAxis />
                    <Radar name="Score" dataKey="A" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                    <Tooltip />
                  </RadarChart>

                  <PieChart width={300} height={300}>
                    <Pie data={pieData} dataKey="value" cx="50%" cy="50%" outerRadius={100} label>
                      {pieData.map((entry, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </div>

                <div className="advanced-metrics">
                  <h4>Advanced Metrics</h4>
                  <ul>
                    <li>Sentiment: <b>{sentimentAnalysis}</b></li>
                    <li>Grammar Score: <b>{grammarScore}%</b></li>
                    <li>ATS Score: <b>{atsScore}%</b></li>
                    <li>Skill Match Score: <b>{skillMatchScore}%</b></li>
                    <li>Readability Score: <b>{readabilityScore}%</b></li>
                  </ul>
                </div>
              </div>
            )}

            {/* AI Chat */}
            {activeTab === "chat" && (
              <div className="chat-tab">
                <h4>AI Resume Chat</h4>
                <div className="chat-box">
                  <div className="messages">
                    <p><b>AI:</b> Candidate shows strong backend skills, weak frontend.</p>
                  </div>
                  <div className="chat-input">
                    <input placeholder="Ask something..." />
                    <button>Send</button>
                  </div>
                </div>
              </div>
            )}

            {/* Comparison */}
            {activeTab === "comparison" && (
              <div className="comparison-tab">
                <h4>Candidate Comparison</h4>
                {comparisonCandidates.length > 1 ? (
                  <table>
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Score</th>
                        <th>Skills</th>
                        <th>Experience</th>
                        <th>Education</th>
                        <th>Projects</th>
                      </tr>
                    </thead>
                    <tbody>
                      {comparisonCandidates.map(c => (
                        <tr key={c.id}>
                          <td>{c.name}</td>
                          <td>{c.score}%</td>
                          <td>--</td>
                          <td>--</td>
                          <td>--</td>
                          <td>--</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : <p>Select 2 or more candidates to compare.</p>}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
