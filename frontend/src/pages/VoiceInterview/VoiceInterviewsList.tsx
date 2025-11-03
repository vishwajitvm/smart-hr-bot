// src/pages/VoiceInterviewsList.tsx
import React, { useEffect } from "react";
import type { CandidateItem } from "./VoiceInterviewsPage";
import "./../css/voiceInterview.css";

interface Props {
  candidates: CandidateItem[];
  onSchedule: (item: CandidateItem) => void;
  onViewDetails: (item: CandidateItem) => void;
  selectedForBulk: string[];
  setSelectedForBulk: React.Dispatch<React.SetStateAction<string[]>>;
}

const VoiceInterviewsList: React.FC<Props> = ({
  candidates,
  onSchedule,
  onViewDetails,
  selectedForBulk,
  setSelectedForBulk,
}) => {
  // Handle card click with Ctrl + Click
  const handleCardClick = (e: React.MouseEvent, candidateId: string) => {
    if (e.ctrlKey) {
      if (selectedForBulk.includes(candidateId)) {
        setSelectedForBulk(selectedForBulk.filter((id) => id !== candidateId));
      } else {
        setSelectedForBulk([...selectedForBulk, candidateId]);
      }
    } else {
      // Normal click opens details
      const clickedCandidate = candidates.find(c => c.candidate.id === candidateId);
      if (clickedCandidate) onViewDetails(clickedCandidate);
    }
  };

  // Deselect all when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest(".candidate-card")) {
        setSelectedForBulk([]);
      }
    };
    document.addEventListener("click", handleClickOutside);
    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, [setSelectedForBulk]);

  return (
    <div className="voice-candidates-grid">
      {candidates.map((item) => {
        const isSelected = selectedForBulk.includes(item.candidate.id);
        return (
          <div
            className={`candidate-card ${isSelected ? "selected-card" : ""}`}
            key={item.candidate.id}
            onClick={(e) => handleCardClick(e, item.candidate.id)}
          >
            <div className="candidate-header">
              <h3>{item.candidate.name}</h3>
              <span className={`status-badge status-${item.candidate.stage_ai_voice_call_status}`}>
                {item.candidate.stage_ai_voice_call_status === 0
                  ? "Pending"
                  : item.candidate.stage_ai_voice_call_status === 1
                  ? "Scheduled"
                  : "Completed"}
              </span>
            </div>
            <p className="candidate-role">{item.candidate.position}</p>
            <p className="candidate-exp">{item.candidate.years_of_experience} yrs experience</p>
            <p className="candidate-contact">
              📧 {item.candidate.email} | 📞 {item.candidate.phone}
            </p>
            <div className="candidate-skills">
              {item.candidate.skills.slice(0, 6).map((skill) => (
                <span key={skill} className="skill-badge">
                  {skill}
                </span>
              ))}
              {item.candidate.skills.length > 6 && (
                <span className="more-skills">+{item.candidate.skills.length - 6}</span>
              )}
            </div>
            <div className="candidate-actions">
              <button className="btn-schedule" onClick={(e) => { e.stopPropagation(); onSchedule(item); }}>
                Schedule
              </button>
              <button className="btn-details" onClick={(e) => { e.stopPropagation(); onViewDetails(item); }}>
                Details
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default VoiceInterviewsList;
