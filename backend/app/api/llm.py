from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm_service import llm_service

router = APIRouter(prefix="/llm", tags=["LLM"])

# ---------- Request Models ----------
class PromptRequest(BaseModel):
    prompt: str

class ChatRequest(BaseModel):
    history: list  # [{"role": "user"/"model", "text": "..."}]
    user_input: str

# ---------- Routes ----------
@router.post("/generate")
async def generate_text(request: PromptRequest):
    """
    Generate text response from Gemini LLM.
    """
    try:
        result = await llm_service.generate_response(request.prompt)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_llm(request: ChatRequest):
    """
    Chat with Gemini using conversation history.
    """
    try:
        result = await llm_service.generate_chat(request.history, request.user_input)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
