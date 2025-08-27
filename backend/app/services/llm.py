# app/services/llm.py
import google.generativeai as genai
from app.core.config import settings
import logging

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
        Generate a text response from Gemini given a prompt.
        """
        try:
            logger.debug(f"Gemini request prompt: {prompt[:200]}...")  # Log first 200 chars
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

# Singleton instance
llm_service = LLMService()

# --- Added wrapper function for backward compatibility ---
async def ask_llm(prompt: str) -> str:
    """
    Wrapper function for generating a response using the LLM.
    This allows other modules to do: from app.services.llm import ask_llm
    """
    return await llm_service.generate_response(prompt)


async def run_interview(candidate_name: str, role: str) -> str:
    return await llm_service.run_interview(candidate_name, role)