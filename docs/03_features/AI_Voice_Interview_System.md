# 🎙️ AI-Driven Voice Interview System — Complete Flow (India Context)

Below is the **complete, realistic, step-by-step flow (India context, Twilio + AssemblyAI + LLM)** explained in plain language.

---

## 🎯 Full Voice Interview Flow — With Question Generation, Calendar Scheduling, Reminders and AI Follow-Ups

---

### 🧩 0. Initial Input (what you already send)

You provide structured candidate + job data like this:

* Candidate profile (skills, summary, experience, score, etc.)
* Job description, requirements, and responsibilities
* Current stage statuses (`stage_ai_voice_call_status`, etc.)

This data is **enough to start** the voice interview process because it has:

* Candidate info (for call setup)
* Job info (for question generation)
* Current evaluation stage (for process branching)

---

### 🧠 1. Question Generation Phase

#### 1.1 Base Questions (AI-Generated)

* The system uses the **LLM (Gemini)** to generate **a base set of 8-12 questions** automatically.
* These questions are tailored using:

  * The **candidate’s resume + skills**
  * The **job description** and seniority level
  * Past interview data (if available)
  * Scoring breakdown (e.g., if soft skills are weak, add behavioral questions)

* Types of questions:

  * Technical (based on job skills)
  * Scenario-based (“What would you do if…”)
  * Behavioral (communication, teamwork)
  * AI-generated custom ones based on project keywords

**Example:**

> “Can you explain your experience integrating RESTful APIs in Node.js?”  
> “Tell me about a time you optimized backend performance.”  
> “How do you handle production deployment and debugging?”

#### 1.2 HR-Added Custom Questions

* The HR panel allows adding **optional custom questions** for this candidate.
* Stored in DB under:

```json
{
  "job_id": "...",
  "candidate_id": "...",
  "custom_questions": ["What was your role in the SetBot project?"]
}
```

* These merge with AI questions before interview starts.

#### 1.3 Final Question Set

Before call initiation:

* System merges → `AI questions + HR questions`
* Applies a **sequence plan** (randomized or weighted order)
* Saves this list as a **Question Plan JSON**:

```json
{
  "interview_id": "xyz123",
  "questions": [
    {"id": 1, "type": "technical", "question": "..."},
    {"id": 2, "type": "hr_custom", "question": "..."}
  ]
}
```

---

### 📅 1.4 Scheduling — Google Calendar & Reminders (NEW / IMPORTANT)

**What happens:**

1. The AI Interview Planner Agent requests available slots (from HR preferences and candidate availability if provided).
2. The Planner creates a **Google Calendar event** using the service account / OAuth flow:
   * Event title: `Smart HR Bot - Interview: <Candidate Name> - <Job Title>`
   * Description: includes `Question Plan` summary, interviewer info, consent text, links to candidate resume and dashboard.
   * Location: phone call (Twilio number) or virtual meeting link if needed.
   * Guests: candidate email (if available), hr_user_id (organizer).
   * Reminders: automatic 12-hour email reminder + configurable minutes-before reminder (e.g., 15 minutes) and SMS via Twilio.

3. The Planner stores the calendar event id and scheduled timestamp in the `interviews` collection.

**Why 12-hour email reminder is important (India context):**

* Many candidates in India prefer an advance reminder so they can prepare and ensure network availability.
* Email reminder includes audio consent info, rescheduling link, and contact details.

**Reminder types created:**

* **12 hours before (email)** — comprehensive reminder with agenda, consent, and reschedule options.
* **X minutes before (SMS via Twilio)** — quick heads-up (configurable, e.g., 15 minutes).
* **Calendar notification** — standard Google Calendar notification (if candidate uses Gmail).

**Stored Reminder Record Example:**

```json
{
  "interview_id": "twilio-call-XXXXX",
  "scheduled_at": "2025-11-02T10:00:00+05:30",
  "calendar_event_id": "abcd1234@google.com",
  "reminders": {
    "email_12h": "2025-11-01T22:00:00+05:30",
    "sms_15m": "2025-11-02T09:45:00+05:30"
  }
}
```

---

### 📞 2. Twilio Voice Call Setup

#### 2.1 Call Initialization

* The backend triggers Twilio’s API to **call the candidate’s phone number** at the scheduled time.
* Twilio connects the candidate to the **AI voice agent** (either using Twilio Studio or Twilio Voice API + a backend voice handler).
* The calendar event and Twilio call are linked by `interview_id`.

#### 2.2 Text-to-Speech (TTS)

* The AI agent “speaks” each question using Twilio’s **TTS engine (Amazon Polly / Google Voice)** or a pre-recorded voice.
* Example: “Hi Vishwajit, this is your Smart HR interview assistant. Let’s begin…”

#### 2.3 Voice Capture (Recording & Media Streams)

* Candidate answers in any supported language (English, Hindi, Marathi, etc.).
* Twilio records the audio file (`.wav` / `.mp3`) and:
  * Either posts a final recording URL to your webhook after call end, **or**
  * Streams audio in real-time (Twilio Media Streams) for streaming STT.
* The backend stores the Twilio `CallSid`, recording URL, and associates it with the `interview_id`.

---

### 🎧 3. AssemblyAI (or Whisper / Deepgram) — Transcription & Translation

#### 3.1 Upload Audio

* The recorded file from Twilio is sent to **AssemblyAI API** for transcription.
* For streaming (real-time) flow, audio chunks are streamed to AssemblyAI real-time endpoints.

#### 3.2 Multilingual Handling

* **AssemblyAI supports Hindi and Marathi** and can auto-detect language segments.
* If a candidate speaks Marathi/Hindi, AssemblyAI can:
  * Provide the native-language transcript.
  * Provide an English translation (if requested).
* If AssemblyAI does not detect or translation confidence is low, the system can **fallback to a secondary STT provider** or queue for manual review.

**AssemblyAI response includes:**

* `language_detected` (e.g., `hi`, `mr`, `en`)
* `transcript` (native)
* `translation` (optional English version)
* `confidence` (per-segment)
* `timestamps` (start/end per phrase)
* `speaker_labels` (if diarization enabled)
* `sentiment` (per sentence/segment, optional)

#### 3.3 Output Data Stored

```json
{
  "question_id": 1,
  "audio_url": "twilio/recording123.wav",
  "transcript": "...",
  "translation": "...",
  "language": "hi",
  "sentiment": "positive",
  "stt_confidence": 0.94
}
```

---

### 🤖 4. AI Analysis Phase (LLM-Based Evaluation)

#### 4.1 Question-by-Question Evaluation

The AI evaluates each answer using a **scoring rubric**:

* **Relevance** — matches question and job requirements
* **Depth** — technical detail and examples
* **Communication clarity** — structure & articulation
* **Confidence & sentiment** — assertiveness & positivity
* **Language fluency** — grammar & spoken clarity
* **Cultural fit / tone** — professionalism and attitude
* **Completeness** — addresses all parts of the question
* **Factual correctness** — for technical claims (where verifiable)

**Example per-question score object:**

```json
{
  "question_id": 2,
  "answer_quality": 0.8,
  "confidence": 0.9,
  "technical_depth": 0.7,
  "overall_score": 8.2,
  "evidence": "LLM explanation of why answer is correct or missing parts"
}
```

#### 4.2 Follow-Up Question Generation (Dynamic)

* After each answer, the AI can **generate a contextual follow-up question**.
* Follow-ups are generated only if:
  * The answer is short/ambiguous
  * The scoring rubric requests clarification
  * The job requires deeper probing on a specific skill

**Example flow:**
* Q: “Tell me about your Node.js experience.”  
* A: “I built APIs using Express.js.”  
* AI Follow-up: “Can you explain how you handled authentication and JWTs?”


#### 4.3 How LLMs work here (in very simple terms)

1. We send the question + candidate answer (and optional translated text) to the LLM.
2. The LLM summarizes the answer and checks for keywords, technical concepts, and correctness.
3. It returns:
   * A short explanation (why the score was given)
   * A numeric sub-score for each rubric item
   * Suggested follow-up questions (if needed)

---

### 📊 5. Summary and Scoring

#### 5.1 Aggregated Interview Report

AI compiles:

* Average score across all questions
* Sub-scores (technical, communication, problem-solving, domain relevance)
* Strengths and weaknesses
* Sentiment summary
* Language detection & translation note
* Confidence & clarity metrics
* Recommended next step (e.g., Technical Interview, Reject, Manager Round)

#### 5.2 JSON Summary (for HR Dashboard)

```json
{
  "overall_score": 82,
  "technical_score": 80,
  "communication_score": 85,
  "sentiment": "positive",
  "key_strengths": ["clarity", "depth of answers"],
  "weak_areas": ["project detail explanation"],
  "fitment": "Strong"
}
```

#### 5.3 Visual Report

Frontend can show:

* 📈 Bar chart per skill/topic
* 🧠 Word cloud of strong concepts
* ❤️ Sentiment graph over time
* 🗣️ Transcript + translation viewer
* 🔊 Audio playback with per-question jump links

---

### 🗂️ 6. Storage, Audit & Next Steps

1. **Store everything in MongoDB** (you use GridFS for audio):
   * Candidate metadata
   * Question plan
   * Calendar event id & reminders
   * Transcripts + translations
   * Audio binary (GridFS) + recording metadata (Twilio CallSid)
   * Scoring breakdowns + evidence
   * Audit & consent logs

2. **Update stages** after successful run:
   * `stage_ai_voice_call_status: 1`
   * `stage_ai_screening_status: 1`

3. **Notifications**:
   * **12-hour email reminder** (sent at scheduling time via Google Calendar email or your mail server)
   * **15-minute SMS reminder** (sent via Twilio)
   * **Completion notification** to HR via email + dashboard alert

4. **Audit & Compliance**:
   * Store `consent_recorded`, `consent_timestamp`, `pipeline_run_id`, and model/prompt versions
   * Maintain `model_versions` collection with prompt hashes for explainability

---

### 🚀 7. Summary Flow — In Simple Words

| Step | What Happens                           | Who Does It      |
| ---- | -------------------------------------- | ---------------- |
| 1    | System reads candidate + job data      | Backend          |
| 2    | AI creates base questions              | LLM              |
| 3    | HR adds optional custom questions      | HR Dashboard     |
| 4    | Planner schedules Google Calendar event (adds reminders) | Planner Agent |
| 5    | Twilio calls candidate at scheduled time | Backend + Twilio |
| 6    | Candidate answers verbally             | Candidate        |
| 7    | Twilio records & sends audio           | Twilio           |
| 8    | AssemblyAI transcribes & translates    | AssemblyAI       |
| 9    | AI analyses each answer & follow-ups   | LLM              |
| 10   | Scores, transcript, and summary stored | Backend          |
| 11   | HR views result dashboard              | HR Portal        |

---

*Author: Vishwajit*  
*Date: 2025-10-30*
