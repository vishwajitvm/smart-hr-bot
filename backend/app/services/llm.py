import google.generativeai as genai
from app.core.config import settings
from app.models.job_ai import JobAIRequest, JobAISuggestion
from app.chains.job_prompt import job_prompt
import logging, uuid, json, re, asyncio
from tenacity import retry, wait_exponential, stop_after_attempt

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """Custom error for LLM failures."""


class LLMService:
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"✅ Gemini LLM initialized with model: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {str(e)}")
            raise LLMServiceError("Failed to initialize Gemini")

    @staticmethod
    def _extract_text(response) -> str:
        """Extract plain text from Gemini response."""
        try:
            return response.candidates[0].content.parts[0].text.strip()
        except Exception:
            raise LLMServiceError("Gemini returned no usable content")

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
    async def generate_response(self, prompt: str) -> str:
        """Generate plain text response with retries and async safe call."""
        logger.debug(f"Gemini request prompt: {prompt[:200]}...")

        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            text = self._extract_text(response)
            logger.debug(f"Gemini response: {text[:200]}...")
            return text
        except Exception as e:
            logger.error(f"❌ Error in Gemini generate_response: {str(e)}")
            raise LLMServiceError("Failed to generate response")

    async def generate_chat(self, history: list, user_input: str) -> str:
        """Generate conversational response given chat history + input."""
        logger.debug(f"Chat history size={len(history)}, User input: {user_input[:100]}")

        try:
            chat = self.model.start_chat(history=[
                {"role": h["role"], "parts": [h["text"]]} for h in history
            ])
            response = await asyncio.to_thread(chat.send_message, user_input)
            return self._extract_text(response)
        except Exception as e:
            logger.error(f"❌ Error in Gemini generate_chat: {str(e)}")
            raise LLMServiceError("Failed to generate chat response")
        
    # Expose sanitizer for external use
    def sanitize_json(self, raw_text: str) -> dict:
        return _sanitize_json_output(raw_text)


# --- Utilities ---
def _sanitize_json_output(raw_text: str) -> dict:
    logger.debug(f"🔍 Raw LLM output before cleaning: {raw_text[:500]}")
    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```[a-zA-Z]*\n?", "", raw_text)
        raw_text = raw_text.rstrip("`").strip()

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match:
        raw_text = match.group(0)

    logger.debug(f"🧹 Cleaned JSON candidate: {raw_text[:500]}")

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parse error: {e} | Raw: {raw_text[:500]}")
        raise LLMServiceError("Invalid JSON returned by Gemini")

        

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
    
# Singleton
llm_service = LLMService()