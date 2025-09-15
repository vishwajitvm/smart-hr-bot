import { useState, useEffect } from "react";
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  PieChart, Pie, Cell, Tooltip,
  BarChart, Bar, XAxis, YAxis
} from "recharts";
import { fetchCandidatesWithScores, fetchCandidateWithScoreById } from "../services/api";
import "./css/ResumeScoring.css";

export default function ResumeScoringDashboard() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("details");
  const [comparisonCandidates, setComparisonCandidates] = useState<any[]>([]);
  const [pagination, setPagination] = useState({
    totalCount: 0,
    totalPages: 1,
    currentPage: 1,
    hasMore: false,
  });

  const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff8042", "#0088FE", "#FFBB28", "#FF8042"];

  useEffect(() => {
    loadCandidates(1);
  }, []);

  const loadCandidates = async (page: number) => {
    try {
      const res: any = await fetchCandidatesWithScores(page, 2);
      if (res?.data?.candidates) {
        setCandidates(res.data.candidates);
        setPagination({
          currentPage: res.data.pagination?.currentPage ?? 1,
          totalPages: res.data.pagination?.totalPages ?? 1,
          totalCount: res.data.pagination?.totalCount ?? 0,
          hasMore: res.data.pagination?.hasMore ?? false,
        });
      }
    } catch (err) {
      console.error("Failed to fetch candidates", err);
    }
  };

  const renderPagination = () => {
    const pages = [];
    const { currentPage, totalPages } = pagination;
    const maxVisible = 5; // show 5 pages around current

    let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);

    if (end - start < maxVisible - 1) {
      start = Math.max(1, end - maxVisible + 1);
    }

    if (start > 1) pages.push(<span key="first">1 ...</span>);

    for (let i = start; i <= end; i++) {
      pages.push(
        <button
          key={i}
          className={i === currentPage ? "active" : ""}
          onClick={() => loadCandidates(i)}
        >
          {i}
        </button>
      );
    }

    if (end < totalPages) pages.push(<span key="last">... {totalPages}</span>);

    return pages;
  };


  const viewCandidateDetails = async (candidateId: string) => {
    try {
      const res: any = await fetchCandidateWithScoreById(candidateId);
      const candidateData = res?.data?.candidates?.[0];
      if (!candidateData) return;

      // Normalize structure
      setSelectedCandidate({
        candidate: candidateData.candidate ?? {},
        job: candidateData.job ?? {},
        score: candidateData.score ?? {},
      });
      setActiveTab("details");
    } catch (err) {
      console.error("Failed to fetch candidate details", err);
    }
  };

  return (
    <div className="resume-dashboard">
      {/* Filters Panel */}
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
          {candidates.map(c => <option key={c.candidate.id}>{c.job?.title ?? "N/A"}</option>)}
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

      {/* Results Panel */}
      <div className="results">
        <h2>Resume Scoring Results</h2>

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
              <tr key={c.candidate.id}>
                <td>{c.candidate?.name ?? "N/A"}</td>
                <td>{c.candidate?.email ?? "N/A"}</td>
                <td>{c.job?.title ?? "N/A"}</td>
                <td>{c.score?.overall_score ?? 0}%</td>
                <td>
                  <button onClick={() => viewCandidateDetails(c.candidate.id)}>View</button>
                </td>
                <td>
                  <input
                    type="checkbox"
                    onChange={(e) => {
                      if (e.target.checked)
                        setComparisonCandidates([...comparisonCandidates, c]);
                      else
                        setComparisonCandidates(
                          comparisonCandidates.filter(cc => cc.candidate.id !== c.candidate.id)
                        );
                    }}
                  />
                </td>
              </tr>

            ))}
            {/* Pagination Row */}
            <tr>
              <td colSpan={6} style={{ textAlign: "center" }}>
                <div className="pagination">
                  <button
                    disabled={pagination.currentPage === 1}
                    onClick={() => loadCandidates(pagination.currentPage - 1)}
                  >
                    Previous
                  </button>

                  {renderPagination()}

                  <button
                    disabled={pagination.currentPage === pagination.totalPages}
                    onClick={() => loadCandidates(pagination.currentPage + 1)}
                  >
                    Next
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>


        {/* Selected Candidate Details */}
        {selectedCandidate && (
          <div className="candidate-details">
            <div className="tabs">
              <button className={activeTab === "details" ? "active" : ""} onClick={() => setActiveTab("details")}>Details & Scoring</button>
              <button className={activeTab === "chat" ? "active" : ""} onClick={() => setActiveTab("chat")}>AI Chat</button>
              <button className={activeTab === "comparison" ? "active" : ""} onClick={() => setActiveTab("comparison")}>Comparison</button>
            </div>

            {/* Details Tab */}
            {activeTab === "details" && (
              <div className="details-tab">
                <h3>{selectedCandidate.candidate?.name ?? "N/A"}</h3>

                <div className="charts">
                  {selectedCandidate.score?.scoring_breakdown ? (
                    <>
                      {/* Radar Chart */}
                      <div className="chart-wrapper">
                        <RadarChart
                          key={selectedCandidate.candidate.id}
                          outerRadius={100}
                          width={400}
                          height={300}

                          data={Object.entries(selectedCandidate.score.scoring_breakdown).map(([k, v]) => ({ subject: k, A: v }))}
                        >
                          <PolarGrid />
                          <PolarAngleAxis dataKey="subject" />
                          <PolarRadiusAxis />
                          <Radar name="Score" dataKey="A" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                          <Tooltip />
                        </RadarChart>
                      </div>

                      {/* Pie Chart */}
                      <div className="chart-wrapper">

                        <PieChart width={300} height={300}>
                          <Pie
                            key={selectedCandidate.candidate.id}
                            data={Object.entries(selectedCandidate.score.scoring_breakdown).map(([k, v]) => ({ name: k, value: v }))}
                            dataKey="value"
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            label
                          >
                            {Object.entries(selectedCandidate.score.scoring_breakdown).map((_, index) => (
                              <Cell key={index} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </div>

                      {/* Additional Bar Chart */}
                      <div className="chart-wrapper">

                        <BarChart
                          width={500}
                          height={300}
                          data={Object.entries(selectedCandidate.score.scoring_breakdown).map(([k, v]) => ({ name: k, score: v }))}
                          margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
                        >
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="score" fill="#82ca9d" />
                        </BarChart>
                      </div>
                    </>
                  ) : (
                    <p>No scoring data available.</p>
                  )}
                </div>

                {/* Advanced Metrics Table */}
                <div className="advanced-metrics">
                  <h4>Candidate Detailed Metrics</h4>
                  <table className="metrics-table">
                    <tbody>
                      {/* Recommendation first */}
                      <tr>
                        <td>Recommendation</td>
                        <td>{selectedCandidate.score?.recommendation ?? "N/A"}</td>
                      </tr>

                      {/* Fitment Status */}
                      <tr>
                        <td>Fitment Status</td>
                        <td>{selectedCandidate.score?.fitment_status ?? "N/A"}</td>
                      </tr>

                      {/* Fitment Score */}
                      <tr>
                        <td>Fitment Score</td>
                        <td>
                          <div className="progress-bar-container">
                            <div
                              className="progress-bar"
                              style={{ width: `${selectedCandidate.score?.fitment_score ?? 0}%`, backgroundColor: COLORS[0] }}
                            >
                              {selectedCandidate.score?.fitment_score ?? 0}%
                            </div>
                          </div>
                        </td>
                      </tr>

                      {/* Overall Score */}
                      <tr>
                        <td>Overall Score</td>
                        <td>
                          <div className="progress-bar-container">
                            <div
                              className="progress-bar"
                              style={{ width: `${selectedCandidate.score?.overall_score ?? 0}%`, backgroundColor: COLORS[1] }}
                            >
                              {selectedCandidate.score?.overall_score ?? 0}%
                            </div>
                          </div>
                        </td>
                      </tr>

                      {/* Detailed Scoring Breakdown */}
                      {Object.entries(selectedCandidate.score?.scoring_breakdown || {}).map(([key, value], idx) => {
                        const score = Number(value) || 0;
                        return (
                          <tr key={key}>
                            <td>{key.replace(/_/g, " ").toUpperCase()}</td>
                            <td>
                              <div className="progress-bar-container">
                                <div
                                  className="progress-bar"
                                  style={{ width: `${score}%`, backgroundColor: COLORS[(idx + 2) % COLORS.length] }}
                                >
                                  {score}%
                                </div>
                              </div>
                            </td>
                          </tr>
                        );
                      })}

                      {/* Sentiment Analysis */}
                      <tr>
                        <td>Sentiment</td>
                        <td>{selectedCandidate.score?.sentiment?.overall ?? "N/A"}</td>
                      </tr>
                      <tr>
                        <td>Sentiment Tone</td>
                        <td>{selectedCandidate.score?.sentiment?.tone ?? "N/A"}</td>
                      </tr>

                      {/* Strengths & Weaknesses */}
                      <tr>
                        <td>Strengths (Technical)</td>
                        <td>{selectedCandidate.score?.strengths?.technical?.join(", ") || "N/A"}</td>
                      </tr>
                      <tr>
                        <td>Strengths (Soft Skills)</td>
                        <td>{selectedCandidate.score?.strengths?.soft?.join(", ") || "N/A"}</td>
                      </tr>
                      <tr>
                        <td>Weaknesses (Technical)</td>
                        <td>{selectedCandidate.score?.weaknesses?.technical?.join(", ") || "N/A"}</td>
                      </tr>
                      <tr>
                        <td>Weaknesses (Soft Skills)</td>
                        <td>{selectedCandidate.score?.weaknesses?.soft?.join(", ") || "N/A"}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>


              </div>
            )}


            {/* Chat Tab */}
            {activeTab === "chat" && (
              <div className="chat-tab">
                <h4>AI Resume Chat</h4>
                <div className="chat-box">
                  <div className="messages">
                    <p><b>AI:</b> Candidate's profile summary and technical insights will appear here.</p>
                  </div>
                  <div className="chat-input">
                    <input placeholder="Ask something..." />
                    <button>Send</button>
                  </div>
                </div>
              </div>
            )}

            {/* Comparison Tab */}
            {activeTab === "comparison" && (
              <div className="comparison-tab">
                <h4>Candidate Comparison</h4>
                {comparisonCandidates.length > 1 ? (
                  <table>
                    <thead>
                      <tr>
                        <th className="has-text-dark">Name</th>
                        <th className="has-text-dark">Score</th>
                        <th className="has-text-dark">Skills</th>
                        <th className="has-text-dark">Experience</th>
                        <th className="has-text-dark">Education</th>
                        <th className="has-text-dark">Projects</th>
                      </tr>
                    </thead>
                    <tbody>
                      {comparisonCandidates.map(c => (
                        <tr key={c.candidate.id}>
                          <td>{c.candidate?.name ?? "N/A"}</td>
                          <td>{c.score?.overall_score ?? 0}%</td>
                          <td>{c.candidate?.skills?.join(", ") ?? "N/A"}</td>
                          <td>{c.candidate?.years_of_experience ?? "N/A"} yrs</td>
                          <td>{c.candidate?.extra_data?.education?.map((e: any) => e.degree).join(", ") ?? "N/A"}</td>
                          <td>{c.candidate?.extra_data?.projects?.map((p: any) => p.title).join(", ") ?? "N/A"}</td>
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
