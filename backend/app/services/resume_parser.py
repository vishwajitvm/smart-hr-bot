#app\services\resume_parser.py
import os
import json
import logging
import re
from langchain_google_genai import ChatGoogleGenerativeAI

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class ResumeParserService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in environment variables")

        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            google_api_key=api_key
        )

    def _normalize(self, parsed: dict) -> dict:
        """
        Ensure schema consistency:
        - Extract extra emails/phones
        - Collect unexpected fields
        """
        schema = {
            "name": "",
            "email": "",
            "phone": "",
            "location": "",
            "years_of_experience": "",
            "skills": [],
            "experience_summary": "",
            "education": [],
            "projects": [],
            "certifications": [],
            "languages": [],
            "interests": [],
            "hobbies": [],
            "role_specific_highlights": [],
            "other_emails": [],
            "other_phones": [],
            "candidate_other_details": {}
        }

        normalized = schema.copy()

        # --- handle canonical keys first ---
        for key in schema:
            if key in parsed:
                normalized[key] = parsed[key]

        # --- handle multiple emails ---
        if "email" in parsed:
            if isinstance(parsed["email"], list) and parsed["email"]:
                normalized["email"] = parsed["email"][0]  # first is primary
                normalized["other_emails"] = parsed["email"][1:]
            elif isinstance(parsed["email"], str):
                normalized["email"] = parsed["email"]

        # --- handle multiple phones ---
        if "phone" in parsed:
            if isinstance(parsed["phone"], list) and parsed["phone"]:
                normalized["phone"] = parsed["phone"][0]
                normalized["other_phones"] = parsed["phone"][1:]
            elif isinstance(parsed["phone"], str):
                normalized["phone"] = parsed["phone"]

        # --- collect unexpected fields ---
        for key, value in parsed.items():
            if key not in normalized:
                normalized["candidate_other_details"][key] = value

        return normalized

    def parse_resume(self, text: str) -> dict:
        """Parse resume text into structured JSON"""
        prompt = f"""
        You are a strict Resume Parser.
        You must return ONLY valid JSON (no explanations, no natural text).
        Always pick the most likely single value for fields (e.g., one name, one email, one phone).
        If multiple values exist for email/phone, return them as an array.

        Required schema:
        {{
          "name": "<full name or list if multiple>",
          "email": "<email or list if multiple>",
          "phone": "<phone or list if multiple>",
          "location": "<city, country>",
          "years_of_experience": "<number of years if available>",
          "skills": ["skill1", "skill2", "skill3"],
          "experience_summary": "<summary of experience>",
          "education": [
            {{
              "degree": "<degree>",
              "institution": "<school/university>",
              "year": "<year if available>"
            }}
          ],
          "projects": [
            {{
              "title": "<project name>",
              "description": "<short description>",
              "technologies": ["tech1", "tech2"]
            }}
          ],
          "certifications": ["certification1", "certification2"],
          "languages": ["English", "French", "Spanish"],
          "interests": ["interest1", "interest2"],
          "hobbies": ["hobby1", "hobby2"],
          "role_specific_highlights": ["<highlight1>", "<highlight2>"]
        }}

        Resume text:
        {text}
        """

        try:
            response = self.llm.invoke(prompt)

            if hasattr(response, "content"):
                parsed_text = (
                    response.content[0].text
                    if isinstance(response.content, list)
                    else response.content
                )
            else:
                parsed_text = str(response)

            parsed_text = parsed_text.strip()
            logging.info(f"Raw LLM output: {parsed_text}")

            # clean markdown fences
            cleaned = re.sub(r"^```(?:json)?", "", parsed_text, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()

            parsed = json.loads(cleaned)

            return self._normalize(parsed)

        except Exception as e:
            logging.error(f"Parsing failed: {e}", exc_info=True)
            return {
                "name": "",
                "email": "",
                "phone": "",
                "location": "",
                "years_of_experience": "",
                "skills": [],
                "experience_summary": "",
                "education": [],
                "projects": [],
                "certifications": [],
                "languages": [],
                "interests": [],
                "hobbies": [],
                "role_specific_highlights": [],
                "other_emails": [],
                "other_phones": [],
                "candidate_other_details": {}
            }
