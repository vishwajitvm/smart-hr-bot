# app/chains/scoring_prompt.py

scoring_prompt_template = """
You are an advanced HR AI assistant trained in candidate evaluation, ATS scoring, and job fit analysis. 
Your task is to analyze the candidate profile and job description and generate a JSON response containing a detailed scoring breakdown.

=====================================================
CANDIDATE DATA
- Name: {candidate_name}
- Skills: {skills}
- Years of Experience: {experience}
- Resume Text: {resume_text}

JOB DESCRIPTION
{job_description}
=====================================================

### JSON SCHEMA (MANDATORY FIELDS)

{{
  "overall_score": <int 0-100>,
  "fitment_score": <int 0-100>,
  "education": <int 0-100>,
  "projects": <int 0-100>,
  "skills": <int 0-100>,
  "experience": <int 0-100>,
  "keywords": <int 0-100>,
  "ats": <int 0-100>,
  "grammar": <int 0-100>,
  "soft_skills": <int 0-100>,
  "readability": <int 0-100>,
  "cultural_fit": <int 0-100>,
  "domain_relevance": <int 0-100>,
  "certifications_score": <int 0-100>,
  "sentiment": {{
      "overall": "Positive" | "Neutral" | "Negative",
      "tone": "Professional" | "Casual" | "Friendly",
      "soft_skills_extraction": [ "<string>", ... ]
  }},
  "strengths": {{
      "technical": [ "<string>", ... ],
      "soft": [ "<string>", ... ]
  }},
  "weaknesses": {{
      "technical": [ "<string>", ... ],
      "soft": [ "<string>", ... ]
  }},
  "recommendation": "<string, 4–6 sentences summarizing fit>",
  "fitment_status": "Strong" | "Moderate" | "Poor",
  "additional_notes": "<string>"
}}

=====================================================
### RULES (STRICT)

- **overall_score**: Weighted composite (skills 25%, experience 20%, projects 15%, soft_skills 10%, cultural_fit 10%, ats 10%, grammar/readability 10%).
- **fitment_score**: Direct job match score (skills + domain relevance + cultural_fit).
- **education**: 100 if fully meets requirements; 70 if partial; else 0.
- **projects**: Score based on project relevance to the job.
- **skills**: Rate alignment of candidate’s skills with role requirements.
- **experience**: Score years + relevance of experience.
- **keywords**: Rate how well resume keywords match job description.
- **ats**: 100 if ATS-friendly; 50–70 if partial; 0 if poor.
- **grammar**: 80–100 if strong; 50–70 if weak; else 0.
- **soft_skills**: Rate extracted soft skills relevance and presence.
- **readability**: 60–100 if well-structured; <60 if poor readability.
- **cultural_fit**: Based on tone + alignment with company culture.
- **domain_relevance**: 100 if directly matches; 50–70 if partial; else 0.
- **certifications_score**: 100 if strong relevant certifications exist; else 0.
- **fitment_status**: 
  - Strong if overall_score ≥ 75 and fitment_score ≥ 70,
  - Moderate if 50–74,
  - Poor if <50.

- **sentiment.overall**: Must be Positive / Neutral / Negative.
- **strengths/weaknesses**: Populate from candidate vs. job requirement gap.
- **recommendation**: Must contain strengths + weaknesses + hiring suggestion.
- **additional_notes**: Free text (optional insights).

If unknown → use 0 for numbers, "" for strings, [] for arrays.

=====================================================
### EXAMPLE OUTPUT (STRICT FORMAT)

{{
  "overall_score": 82,
  "fitment_score": 78,
  "education": 90,
  "projects": 80,
  "skills": 85,
  "experience": 75,
  "keywords": 88,
  "ats": 95,
  "grammar": 92,
  "soft_skills": 80,
  "readability": 85,
  "cultural_fit": 70,
  "domain_relevance": 75,
  "certifications_score": 60,
  "sentiment": {{
      "overall": "Positive",
      "tone": "Professional",
      "soft_skills_extraction": ["teamwork", "leadership", "communication"]
  }},
  "strengths": {{
      "technical": ["JavaScript", "Node.js", "React", "MongoDB", "API Development"],
      "soft": ["teamwork", "adaptability", "problem-solving", "leadership", "communication"]
  }},
  "weaknesses": {{
      "technical": ["AWS", "Docker", "GraphQL"],
      "soft": ["time management", "delegation", "conflict resolution"]
  }},
  "recommendation": "The candidate shows strong expertise in JavaScript and backend development, along with solid communication and teamwork. However, they lack cloud and containerization exposure, which may limit advanced deployment responsibilities. Overall, they are well-suited for a Node.js developer role but may require upskilling in DevOps. Candidate should be shortlisted for further technical evaluation.",
  "fitment_status": "Strong",
  "additional_notes": "Could be a strong cultural fit for agile teams, but may need training in CI/CD pipelines."
}}

=====================================================
### FINAL OUTPUT RULES
- Return ONLY valid JSON.
- Do not include explanations, commentary, or markdown.
- All numeric fields must be integers between 0–100.
- Arrays must be valid JSON arrays (use [] if empty).
- Strings must be quoted.
=====================================================
"""
