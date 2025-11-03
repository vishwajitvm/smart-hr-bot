import React, { useEffect, useState } from "react";
import VoiceInterviewsList from "./VoiceInterviewsList";
import InterviewDetailsModal from "./InterviewDetailsModal";
import Swal from "sweetalert2";
import "./../css/voiceInterview.css";
import { initiateVoiceInterview, fetchApprovedCandidates } from "../../services/api";

export interface CandidateItem {
  candidate: {
    name: string;
    email: string;
    phone: string;
    location: string;
    years_of_experience: number;
    skills: string[];
    experience_summary: string;
    position: string;
    job_id: string;
    status: string;
    deleted: boolean;
    resume_id?: string;
    resume_url?: string;
    stage_resume_review_status?: number;
    stage_ai_voice_call_status?: number;
    stage_ai_screening_status?: number;
    extra_data?: any;
    id: string;
  };
  job: {
    title: string;
    department?: string;
    location?: string;
    workMode?: string;
    type?: string;
    experience?: string;
    openings?: number;
    salary?: string;
    deadline?: string;
    description?: string;
    responsibilities?: string;
    requirements?: string;
    benefits?: string;
    id?: string;
  };
  resume?: any;
  score?: any;
}

const VoiceInterviewsPage: React.FC = () => {
  const [candidates, setCandidates] = useState<CandidateItem[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateItem | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [selectedForBulk, setSelectedForBulk] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  /* -------------------------------------------------------------------------- */
  /*                           🚀 Fetch Candidates API                           */
  /* -------------------------------------------------------------------------- */
  const loadCandidates = async () => {
    setLoading(true);
    try {
      const response = await fetchApprovedCandidates(1, 20);
      if (response.data?.candidates) {
        setCandidates(response.data.candidates);
      } else {
        setCandidates([]);
      }
    } catch (error: any) {
      Swal.fire({
        icon: "error",
        title: "Failed to load candidates",
        text: error.response?.data?.message || error.message || "An error occurred.",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCandidates();
  }, []);

  /* -------------------------------------------------------------------------- */
  /*                          🧠 Schedule Voice Interview                        */
  /* -------------------------------------------------------------------------- */
  const scheduleInterviews = async (items: CandidateItem[]) => {
    if (!items || items.length === 0) return;

    const result = await Swal.fire({
      title:
        items.length > 1
          ? `Start AI Voice Interviews for ${items.length} candidates?`
          : `Start AI Voice Interview?`,
      html:
        items.length > 1
          ? `<div style="text-align:left;">You are about to initiate AI Voice Interviews for <b>${items.length}</b> candidates.<br/>This will trigger the AI Voice Bot to call each candidate automatically.</div>`
          : `<div style="text-align:left;">
              <b>Candidate:</b> ${items[0].candidate.name}<br/>
              <b>Position:</b> ${items[0].job.title}<br/>
              <b>Experience:</b> ${items[0].candidate.years_of_experience} years<br/>
              This will initiate the AI Voice Interview session via AssemblyAI.
            </div>`,
      icon: "question",
      showCancelButton: true,
      confirmButtonText:
        items.length > 1 ? "Yes, Start All Interviews" : "Yes, Start Interview",
      cancelButtonText: "No, Cancel",
      focusCancel: true,
      reverseButtons: true,
      width: items.length > 1 ? "500px" : undefined,
    });

    if (!result.isConfirmed) return;

    Swal.fire({
      title:
        items.length > 1
          ? "Initializing AI Voice Interviews..."
          : "Initializing AI Voice Interview...",
      text: "Connecting to AssemblyAI and preparing voice bot workflow...",
      icon: "info",
      allowOutsideClick: false,
      showConfirmButton: false,
      didOpen: () => Swal.showLoading(),
    });

    try {
      //  IMPORTANT: Payload must remain unchanged
      const payload = {
        candidates: items.map((i) => ({
          candidate: i.candidate,
          job: i.job,
          resume: i.resume,
          score: i.score,
        })),
      };

      const response = await initiateVoiceInterview(payload);

      //  Success notification
      Swal.fire({
        icon: "success",
        title: items.length > 1 ? "Interviews Initiated!" : "Interview Initiated!",
        html:
          items.length > 1
            ? `<div style="text-align:left;">AI Voice Bot will handle calls for all selected candidates.<br/>Transcripts and analytics will appear soon.</div>`
            : `<div style="text-align:left;">
                 <b>Candidate:</b> ${items[0].candidate.name}<br/>
                 <b>Position:</b> ${items[0].job.title}<br/>
                 <b>Status:</b> ${
                     response.data?.message || "Voice session started successfully"
                   }<br/><br/>
                 The AI Voice Bot will handle the call and transcript will appear soon.
               </div>`,
        toast: true,
        position: "top-end",
        timer: 4000,
        showConfirmButton: false,
        timerProgressBar: true,
      });

      // 🔄 Update local UI state
      setCandidates((prev) =>
        prev.map((c) =>
          items.find((i) => i.candidate.id === c.candidate.id)
            ? { ...c, candidate: { ...c.candidate, stage_ai_voice_call_status: 1 } }
            : c
        )
      );

      setSelectedForBulk([]);

      console.log(" Interview initiation response:", response.data);
    } catch (error: any) {
      console.error("❌ Error initiating interviews:", error);
      Swal.fire({
        icon: "error",
        title: "Failed to Start Interviews",
        text:
          error.response?.data?.message ||
          error.message ||
          "An unexpected error occurred.",
        confirmButtonColor: "#f14668",
      });
    }
  };

  /* -------------------------------------------------------------------------- */
  /*                                 UI Handlers                               */
  /* -------------------------------------------------------------------------- */
  const openDetails = (item: CandidateItem) => {
    setSelectedCandidate(item);
    setIsDetailsOpen(true);
  };

  const closeModals = () => {
    setSelectedCandidate(null);
    setIsDetailsOpen(false);
  };

  const handleExportClick = () => {
    Swal.fire({
      title: "Coming Soon 🚀",
      text: "CSV export functionality will be added soon.",
      icon: "info",
      confirmButtonColor: "#3e8ed0",
    });
  };

  const handleBulkActions = () => {
    if (selectedForBulk.length === 0) {
      Swal.fire({
        title: "No candidates selected",
        text: "Please select at least one candidate to schedule in bulk.",
        icon: "info",
        confirmButtonColor: "#3e8ed0",
      });
      return;
    }
    const items = candidates.filter((c) =>
      selectedForBulk.includes(c.candidate.id)
    );
    scheduleInterviews(items);
  };

  /* -------------------------------------------------------------------------- */
  /*                                 RENDER PAGE                                */
  /* -------------------------------------------------------------------------- */
  return (
    <div className="voice-interviews-page container mt-5">
      <section className="section">
        <div className="level">
          <div className="level-left">
            <h2 className="title is-4 has-text-black">AI Voice Interviews</h2>
          </div>
          {selectedForBulk.length === 0 && (
            <span
              style={{
                fontSize: "0.85rem",
                color: "#777",
                marginLeft: "0.5rem",
              }}
            >
              Hold <b>Ctrl</b> and click candidates to select multiple
            </span>
          )}
          <div className="level-right">
            <div className="buttons">
              <button
                className="button is-light soft-btn"
                onClick={handleExportClick}
              >
                Export CSV
              </button>
              <button
                className="button is-primary soft-btn"
                onClick={handleBulkActions}
                disabled={selectedForBulk.length === 0}
                title={
                  selectedForBulk.length === 0
                    ? "Hold Ctrl and click candidates to select multiple"
                    : "Schedule selected candidates"
                }
              >
                Bulk Schedule
              </button>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="has-text-centered mt-6">
            <p>Loading approved candidates...</p>
          </div>
        ) : (
          <VoiceInterviewsList
            candidates={candidates}
            onSchedule={(item: CandidateItem) => scheduleInterviews([item])}
            onViewDetails={openDetails}
            selectedForBulk={selectedForBulk}
            setSelectedForBulk={setSelectedForBulk}
          />
        )}
      </section>

      {selectedCandidate && (
        <InterviewDetailsModal
          isOpen={isDetailsOpen}
          onClose={closeModals}
          candidate={selectedCandidate}
          onScheduleInterview={(item) => scheduleInterviews([item])}
        />
      )}
    </div>
  );
};

export default VoiceInterviewsPage;
