import { useState, useEffect, useRef } from "react";
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  PieChart, Pie, Cell, Tooltip,
  BarChart, Bar, XAxis, YAxis
} from "recharts";
import { FaRobot, FaUser, FaCheckCircle, FaTimesCircle } from "react-icons/fa";
import { fetchCandidatesWithScores, fetchCandidateWithScoreById, fetchAllJobs, candidateChat, approveCandidate, rejectCandidate } from "../services/api";
import Swal from "sweetalert2";
import "./css/ResumeScoring.css";

export default function ResumeScoringDashboard() {
  const hasFetched = useRef(false);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("details");
  const [comparisonCandidates, setComparisonCandidates] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [pagination, setPagination] = useState({
    totalCount: 0,
    totalPages: 1,
    currentPage: 1,
    hasMore: false,
  });
  const [dateFilter, setDateFilter] = useState("This Week");
  const [customDateRange, setCustomDateRange] = useState({
    from: "",
    to: "",
  });
  const [search, setSearch] = useState("");
  const [jobId, setJobId] = useState("");
  const [minScore, setMinScore] = useState<number | "">("");
  const [maxScore, setMaxScore] = useState<number | "">("");
  const [sentiment, setSentiment] = useState("");
  const limit = 4; // candidates per page
  const [chatMessages, setChatMessages] = useState<{ sender: string; text: string }[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isLoadingChat, setIsLoadingChat] = useState(false);



  const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff8042", "#0088FE", "#FFBB28", "#FF8042"];

  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;

    loadCandidates(1);
    loadJobs();
  }, []);

  const handleSendMessage = async () => {
    if (!chatInput.trim() || !selectedCandidate) return;

    const question = chatInput.trim();

    // Add user's question to UI
    setChatMessages(prev => [...prev, { sender: "You", text: question }]);
    setChatInput("");
    setIsLoadingChat(true);

    try {
      // Call API with full selectedCandidate
      const res: any = await candidateChat(selectedCandidate, question);
      console.log("AI Chat response:", res);


      // const aiResponse = res?.data?.ai_chat ?? { question_answer: "No response" };
      const aiResponse = res?.data?.candidates?.[0]?.ai_chat?.question_answer ?? "No response";
      // console.log("AI Response==>:", aiResponse);

      // Append only question_answer
      setChatMessages(prev => [
        ...prev,
        {
          sender: "AI",
          text: aiResponse,
        }
      ]);
    } catch (err) {
      console.error("Chat failed", err);
      setChatMessages(prev => [...prev, { sender: "AI", text: "Error: Unable to fetch AI response." }]);
    } finally {
      setIsLoadingChat(false);
    }
  };

  const handleApprove = async (id: string) => {
    const result = await Swal.fire({
      title: "Approve Candidate?",
      text: "This action will approve the candidate for the applied job.",
      icon: "success",
      showCancelButton: true,
      confirmButtonText: "Yes, Approve",
      cancelButtonText: "Cancel",
    });

    if (result.isConfirmed) {
      try {
        // Call your API to approve candidate
        await approveCandidate(id); // <-- implement this API call
        Swal.fire("Approved!", "Candidate has been approved.", "success");
        // Optional: refresh list or selectedCandidate
        loadCandidates(pagination.currentPage);
      } catch (err) {
        Swal.fire("Error!", "Failed to approve candidate.", "error");
      }
    }
  };

  const handleReject = async (id: string) => {
    const result = await Swal.fire({
      title: "Reject Candidate?",
      text: "This action will reject the candidate for the applied job.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, Reject",
      cancelButtonText: "Cancel",
    });

    if (result.isConfirmed) {
      try {
        // Call your API to reject candidate
        await rejectCandidate(id); // <-- implement this API call
        Swal.fire("Rejected!", "Candidate has been rejected.", "success");
        // Optional: refresh list or selectedCandidate
        loadCandidates(pagination.currentPage);
      } catch (err) {
        Swal.fire("Error!", "Failed to reject candidate.", "error");
      }
    }
  };



  const loadJobs = async () => {
    try {
      const res: any = await fetchAllJobs();

      // if backend returns { jobs: [...] }
      let allJobs = res?.data?.jobs ?? res?.data ?? [];

      const activeJobs = allJobs.filter((job: any) => job.status === 1);
      console.log("Fetched jobs:", activeJobs);
      setJobs(activeJobs);
    } catch (err) {
      console.error("Failed to fetch jobs", err);
    }
  };



  const loadCandidates = async (page: number) => {
    try {
      const res: any = await fetchCandidatesWithScores(page, limit);
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

  const applyFilters = () => {
    const today = new Date();
    let fromDate: string | null = null;
    let toDate: string | null = null;

    if (dateFilter === "This Week") {
      const firstDayOfWeek = new Date(today);
      firstDayOfWeek.setDate(today.getDate() - today.getDay()); // Sunday as start
      const lastDayOfWeek = new Date(firstDayOfWeek);
      lastDayOfWeek.setDate(firstDayOfWeek.getDate() + 6); // Saturday as end

      fromDate = firstDayOfWeek.toISOString();
      toDate = lastDayOfWeek.toISOString();
    } else if (dateFilter === "This Month") {
      const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1, 0, 0, 0);
      const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0, 23, 59, 59);

      fromDate = firstDayOfMonth.toISOString();
      toDate = lastDayOfMonth.toISOString();
    }
    else if (dateFilter === "Custom Range") {
      fromDate = customDateRange.from ? new Date(customDateRange.from).toISOString() : null;
      toDate = customDateRange.to ? new Date(customDateRange.to).toISOString() : null;
    }

    const payload = {
      page: pagination.currentPage || 1,
      limit: limit,
      filters: {
        search: search || null,
        job_id: jobId || null,
        score: {
          min: minScore || null,
          max: maxScore || null,
        },
        date: {
          range: dateFilter === "Custom Range" ? "custom" : dateFilter === "This Week" ? "week" : "month",
          from: fromDate,
          to: toDate,
        },
        sentiment: sentiment || null,
      },
    };

    console.log("Payload being sent:", payload);
    fetchCandidatesWithScores(payload.page, payload.limit, payload.filters)
      .then(res => setCandidates(res.data.candidates))
      .catch(err => console.error(err));
  };


  const timeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    let interval = Math.floor(seconds / 31536000);
    if (interval >= 1) return `${interval} year${interval > 1 ? "s" : ""} ago`;

    interval = Math.floor(seconds / 2592000);
    if (interval >= 1) return `${interval} month${interval > 1 ? "s" : ""} ago`;

    interval = Math.floor(seconds / 86400);
    if (interval >= 1) return `${interval} day${interval > 1 ? "s" : ""} ago`;

    interval = Math.floor(seconds / 3600);
    if (interval >= 1) return `${interval} hr${interval > 1 ? "s" : ""} ago`;

    interval = Math.floor(seconds / 60);
    if (interval >= 1) return `${interval} min${interval > 1 ? "s" : ""} ago`;

    return "Just now";
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
        <select
          value={dateFilter}
          onChange={(e) => setDateFilter(e.target.value)}
        >
          <option value="This Week">This Week</option>
          <option value="This Month">This Month</option>
          <option value="Custom Range">Custom Range</option>
        </select>

        {/* Render date pickers only when Custom Range is chosen */}
        {dateFilter === "Custom Range" && (
          <div className="custom-date-range">
            <label>From</label>
            <input
              type="date"
              value={customDateRange.from}
              onChange={(e) =>
                setCustomDateRange({ ...customDateRange, from: e.target.value })
              }
            />

            <label>To</label>
            <input
              type="date"
              value={customDateRange.to}
              onChange={(e) =>
                setCustomDateRange({ ...customDateRange, to: e.target.value })
              }
            />
          </div>
        )}

        <label>Candidate Name</label>
        <input
          placeholder="Search by name, email, phone"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <label>Job</label>
        <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
          <option value="">All Jobs</option>
          {jobs.map((job) => (
            <option key={job.id} value={job.id}>
              {job.title}
            </option>
          ))}
        </select>

        <label>Score Range</label>
        <input
          type="number"
          placeholder="Min Score"
          value={minScore}
          onChange={(e) => setMinScore(e.target.value ? Number(e.target.value) : "")}
        />
        <input
          type="number"
          placeholder="Max Score"
          value={maxScore}
          onChange={(e) => setMaxScore(e.target.value ? Number(e.target.value) : "")}
        />

        <label>Sentiment</label>
        <select
          value={sentiment}
          onChange={(e) => setSentiment(e.target.value)}
        >
          <option value="">All</option>
          <option value="Positive">Positive</option>
          <option value="Neutral">Neutral</option>
          <option value="Negative">Negative</option>
        </select>

        <button onClick={applyFilters}>Apply Filters</button>

      </div>

      {/* Results Panel */}
      <div className="results">
        {/* <h2>Resume Scoring Results</h2> */}

        <table className="candidate-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              {/* <th>Phone</th> */}
              <th>Score</th>
              <th>Applied At</th>
              <th>Job</th>
              <th>Action</th>
              <th> </th>
            </tr>
          </thead>
          <tbody>
            {candidates.map(c => (
              <tr key={c.candidate.id}>
                {/* <td>{c.candidate?.name ?? "N/A"}</td> */}
                <td>
                  <span
                    className={`${Number(c.candidate?.stage_resume_review_status) === 1
                        ? "tag-approved"
                        : Number(c.candidate?.stage_resume_review_status) === 2
                          ? "tag-rejected"
                          : "tag-pending"
                      }`}
                  >
                    {c.candidate?.name ?? "N/A"}
                  </span>
                </td>

                <td>{c.candidate?.email ?? "N/A"}</td>
                {/* <td>{c.candidate?.phone ?? "N/A"}</td> */}
                <td>{c.score?.overall_score ?? 0}%</td>
                <td>
                  {c.score?.created_at ? timeAgo(c.score.created_at) : "N/A"}
                </td>
                <td>{c.job?.title ?? "N/A"}</td>
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
                        <td>
                          {selectedCandidate.score?.fitment_status ? (
                            <span
                              className={`fitment-badge ${selectedCandidate.score.fitment_status.toLowerCase()}`}
                            >
                              {selectedCandidate.score.fitment_status}
                            </span>
                          ) : (
                            <span className="fitment-badge default">N/A</span>
                          )}
                        </td>
                      </tr>


                      {/* Sentiment */}
                      <tr>
                        <td>Sentiment</td>
                        <td>
                          {selectedCandidate.score?.sentiment?.overall ? (
                            <span
                              className={`sentiment-badge ${selectedCandidate.score.sentiment.overall.toLowerCase()}`}
                            >
                              {selectedCandidate.score.sentiment.overall}
                            </span>
                          ) : (
                            <span className="sentiment-badge default">N/A</span>
                          )}
                        </td>
                      </tr>

                      {/* Sentiment Tone */}
                      <tr>
                        <td>Sentiment Tone</td>
                        <td>
                          {selectedCandidate.score?.sentiment?.tone ? (
                            <span
                              className={`tone-badge ${selectedCandidate.score.sentiment.tone.toLowerCase()}`}
                            >
                              {selectedCandidate.score.sentiment.tone}
                            </span>
                          ) : (
                            <span className="tone-badge default">N/A</span>
                          )}
                        </td>
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


                    </tbody>
                  </table>
                  <br />
                  <hr />
                  <div className="action-buttons" style={{ display: "flex", justifyContent: "center", marginTop: "20px", gap: "20px" }}>
                    <button
                      className="reject-btn"
                      onClick={() => handleReject(selectedCandidate.candidate.id)}
                    >
                      <FaTimesCircle style={{ marginRight: "5px" }} />
                      Reject
                    </button>
                    <button
                      className="approve-btn"
                      onClick={() => handleApprove(selectedCandidate.candidate.id)}
                    >
                      <FaCheckCircle style={{ marginRight: "5px" }} />
                      Approve
                    </button>
                  </div>
                </div>


              </div>
            )}


            {/* Chat Tab */}
            {activeTab === "chat" && (
              <div className="chat-tab">
                <h3>  Explore <b> {selectedCandidate.candidate?.name ?? "the candidate"}’s </b> profile and technical insights </h3>
                {/* <h4>AI Resume Chat</h4> */}
                <div className="chat-box">
                  <div className="messages">
                    {chatMessages.length === 0 ? (
                      <div className="message ai-message">
                        <FaRobot className="icon" />
                        <div className="message-content">
                          <b>AI:</b> Candidate’s profile summary and technical insights will appear here.
                        </div>
                      </div>
                    ) : (
                      chatMessages.map((msg, idx) => (
                        <div
                          key={idx}
                          className={`message ${msg.sender === "AI" ? "ai-message" : "user-message"}`}
                        >
                          {msg.sender === "AI" ? <FaRobot className="icon" /> : <FaUser className="icon" />}
                          <div className="message-content">
                            <b>{msg.sender}:</b> {msg.text}
                          </div>
                        </div>
                      ))
                    )}
                    {isLoadingChat && (
                      <div className="typing"><i>AI is typing...</i></div>
                    )}
                  </div>

                  <div className="chat-input">
                    <input
                      placeholder="Ask something..."
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                    />
                    <button
                      onClick={handleSendMessage}
                      disabled={isLoadingChat || !chatInput.trim()}
                    >
                      Send
                    </button>
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
