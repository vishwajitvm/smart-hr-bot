import React from "react";
import type { CandidateItem } from "./VoiceInterviewsPage";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  candidate: CandidateItem;
  onScheduleInterview: (candidate: CandidateItem) => void; // ✅ new prop
}

const InterviewDetailsModal: React.FC<Props> = ({
  isOpen,
  onClose,
  candidate,
  onScheduleInterview,
}) => {
  if (!candidate) return null;

  const { candidate: c, job, score } = candidate;

  return (
    <div className={`modal ${isOpen ? "is-active" : ""}`}>
      <div className="modal-background" onClick={onClose}></div>
      <div className="modal-card interview-modal">
        <header className="modal-card-head modal-header-custom">
          <p className="modal-card-title">
            Candidate Details — <span className="highlight">{c.name}</span>
          </p>
          <button className="delete" aria-label="close" onClick={onClose}></button>
        </header>

        <section className="modal-card-body">
          <div className="columns is-variable is-5">
            {/* Left Column — Overview */}
            <div className="column is-one-third">
              <div className="box info-box">
                <p className="title is-6 section-title">
                  <strong>Position</strong>
                </p>
                <p>{c.position || job.title}</p>
                <hr />
                <p className="title is-6 section-title">
                  <strong>Email</strong>
                </p>
                <p>{c.email}</p>
                <p className="title is-6 section-title">
                  <strong>Phone</strong>
                </p>
                <p>{c.phone}</p>
                <hr />
                <p className="title is-6 section-title">
                  <strong>Experience</strong>
                </p>
                <p>{c.years_of_experience} years</p>
                <hr />
                <p className="title is-6 section-title">
                  <strong>Score</strong>
                </p>
                <p className="score-highlight">{score?.overall_score ?? "-"}</p>
                <p className="muted-small">
                  Fitment: {score?.fitment_score ?? "-"}
                </p>
              </div>
            </div>

            {/* Right Column — Summary & Details */}
            <div className="column">
              <div className="box content-box">
                <h4 className="title is-6 section-title">Summary</h4>
                <p className="muted">
                  {c.experience_summary?.replace(/\.\.\.$/, "")}
                </p>

                <h4 className="title is-6 section-title">Skills</h4>
                <div className="tags">
                  {c.skills.map((s, i) => (
                    <span key={i} className="tag skill-chip">
                      {s}
                    </span>
                  ))}
                </div>

                <h4 className="title is-6 section-title">Projects</h4>
                <div>
                  {(c.extra_data?.projects || []).map((p: any, i: number) => (
                    <div key={i} className="project-item">
                      <p className="has-text-weight-semibold">{p.title}</p>
                      <p className="muted-small">{p.description}</p>
                    </div>
                  ))}
                </div>

                <h4 className="title is-6 section-title">Recommendation</h4>
                <p>{score?.recommendation}</p>
              </div>
            </div>
          </div>
        </section>

        {/* ✅ Footer Buttons */}
        <footer className="modal-card-foot modal-footer-custom">
          <button
            className="button is-success soft-btn"
            onClick={() => onScheduleInterview(candidate)}
          >
            📅 Schedule Voice Interview
          </button>
          <button className="button is-danger soft-btn" onClick={onClose}>
            Close
          </button>
        </footer>
      </div>
    </div>
  );
};

export default InterviewDetailsModal;
