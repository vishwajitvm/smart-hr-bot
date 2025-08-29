import os
import json
import logging
import re
from langchain_google_genai import ChatGoogleGenerativeAI

logging.basicConfig(
    filename="app.log",
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

    def parse_resume(self, text: str) -> dict:
        """Parse resume text into structured JSON"""
        prompt = f"""
        You are a professional Resume Parser.
        Extract ONLY this JSON (no text, no markdown):

        {{
          "name": "<full name>",
          "email": "<email address>",
          "phone": "<phone number>",
          "location": "<city/country if available>",
          "skills": ["skill1", "skill2", "skill3"],
          "experience": "<summary of experience>"
        }}

        Resume text:
        {text}
        """

        try:
            response = self.llm.invoke(prompt)

            # ✅ Handle different response formats
            if hasattr(response, "content"):
                if isinstance(response.content, list):
                    parsed_text = response.content[0].text
                else:
                    parsed_text = response.content
            else:
                parsed_text = str(response)

            parsed_text = parsed_text.strip()
            logging.info(f"Raw LLM output: {parsed_text}")

            # ✅ Remove markdown fences like ```json ... ```
            cleaned = re.sub(r"^```(?:json)?", "", parsed_text, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()

            # ✅ Load as JSON
            return json.loads(cleaned)

        except Exception as e:
            logging.error(f"Parsing failed: {e}", exc_info=True)
            return {
                "name": "",
                "email": "",
                "phone": "",
                "location": "",
                "skills": [],
                "experience": ""
            }
