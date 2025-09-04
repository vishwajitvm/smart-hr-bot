import google.generativeai as genai
from app.core.config import settings
from app.models.job_ai import JobAIRequest, JobAISuggestion
from app.chains.job_prompt import job_prompt
import logging
import uuid
import json
import re 
from fastapi import HTTPException 

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        try:
            # Configure Gemini
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"✅ Gemini LLM initialized with model: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {str(e)}")
            raise

    async def generate_response(self, prompt: str) -> str:
        """
        Generate a plain text response from Gemini given a prompt.
        """
        try:
            logger.debug(f"Gemini request prompt: {prompt[:200]}...")
            response = self.model.generate_content(prompt)

            if response and response.candidates:
                text = response.candidates[0].content.parts[0].text
                logger.debug(f"Gemini response: {text[:200]}...")
                return text
            else:
                logger.warning("⚠️ Gemini returned empty response.")
                return "Sorry, I couldn’t generate a response."
        except Exception as e:
            logger.error(f"❌ Error in Gemini generate_response: {str(e)}")
            return "An error occurred while generating response."

    async def generate_chat(self, history: list, user_input: str) -> str:
        """
        Generate a conversational response given chat history + user input.
        History is expected as a list of dicts: [{"role": "user"/"model", "text": "..."}]
        """
        try:
            logger.debug(f"Chat history: {history}, User input: {user_input}")

            chat = self.model.start_chat(history=[
                {"role": h["role"], "parts": [h["text"]]} for h in history
            ])

            response = chat.send_message(user_input)

            if response and response.candidates:
                text = response.candidates[0].content.parts[0].text
                logger.debug(f"Gemini chat response: {text[:200]}...")
                return text
            else:
                logger.warning("⚠️ Gemini returned empty chat response.")
                return "Sorry, I couldn’t generate a chat response."
        except Exception as e:
            logger.error(f"❌ Error in Gemini generate_chat: {str(e)}")
            return "An error occurred while processing chat."
        

async def run_interview(candidate_name: str, role: str) -> str:
    """
    Generate a simple interview starter message for a candidate.
    """
    prompt = f"""
You are an interviewer. Start a professional interview with {candidate_name} for the role of {role}.
Return only the first interviewer question, not the entire interview.
"""
    try:
        response = llm_service.model.generate_content(prompt)

        if not response or not response.candidates:
            raise ValueError("Empty response from Gemini")

        text = response.candidates[0].content.parts[0].text
        return text.strip()
    except Exception as e:
        logger.error(f"❌ Error in run_interview: {str(e)}")
        return "Failed to start interview."



# Singleton instance
llm_service = LLMService()


# --- Wrapper for backward compatibility ---
async def ask_llm(prompt: str) -> str:
    """
    Wrapper function for generating a response using the LLM.
    Usage: from app.services.llm import ask_llm
    """
    return await llm_service.generate_response(prompt)


# --- Job generation logic using Gemini ---
async def generate_job_with_ai(request: JobAIRequest) -> JobAISuggestion:
    """
    Generate structured job description using Gemini with JSON output.
    Ensures valid JSON by cleaning fences/extra text.
    """
    structured_prompt = job_prompt.format(title=request.title)

    try:
        response = llm_service.model.generate_content(structured_prompt)

        if not response or not response.candidates:
            raise ValueError("Empty response from Gemini")

        text = response.candidates[0].content.parts[0].text.strip()
        logger.info(f"Raw Gemini job response: {text[:300]}...")

        # --- Sanitize output ---
        # Remove ```json or ``` fences
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = text.rstrip("`").strip()

        # Extract JSON block if extra text exists
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)

        # Try parsing response into JSON
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Gemini JSON: {e} | Raw text: {text}")
            raise HTTPException(status_code=500, detail="AI did not return valid JSON")

        # Add unique AI token (not persisted in DB)
        data["token"] = str(uuid.uuid4())

        return JobAISuggestion(**data)

    except Exception as e:
        logger.error(f"❌ Error in generate_job_with_ai: {e}")
        raise HTTPException(status_code=500, detail=str(e))