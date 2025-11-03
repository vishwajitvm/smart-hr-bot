# backend/app/chains/candidate_chat_chain.py
import logging
import re
import json
from datetime import datetime
from app.services.llm import llm_service
from app.chains.candidate_chat_prompt import candidate_chat_prompt
from app.core.db import chatlogs_collection

logger = logging.getLogger(__name__)


# --- Local Utilities for Candidate Chat Only ---
async def generate_response(prompt: str) -> str:
    """
    Wrapper around llm_service.generate_response.
    Keeps candidate_chat_chain independent of external LLM code changes.
    """
    try:
        logger.info("▶️ generate_response called")
        logger.debug(f"📝 Full Prompt Sent to LLM:\n{prompt}")
        text = await llm_service.generate_response(prompt)
        logger.info("✅ Raw response received from LLM")
        logger.debug(f"🤖 Full Raw LLM Response:\n{text}")
        return text
    except Exception as e:
        logger.error(f"❌ Error in generate_response (candidate_chat_chain): {e}")
        logger.exception("💥 Traceback in generate_response:")
        return "{}"  # return empty JSON string fallback


def sanitize_json(raw_text: str) -> dict:
    """
    Cleans LLM output and ensures valid JSON.
    Extracts first {...} block, strips markdown/code fences.
    """
    try:
        logger.info("▶️ sanitize_json called")
        logger.debug(f"🔍 Raw Input Text Before Cleaning:\n{raw_text}")

        # Remove ```json or ``` fences
        if raw_text.startswith("```"):
            logger.debug("⚠️ Detected markdown/code fences, cleaning them out...")
            raw_text = re.sub(r"^```[a-zA-Z]*\n?", "", raw_text)
            raw_text = raw_text.rstrip("`").strip()

        # Extract first JSON object
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            raw_text = match.group(0)
            logger.debug(f"🧩 Extracted JSON Block:\n{raw_text}")
        else:
            logger.warning("⚠️ No JSON object found in response!")

        parsed = json.loads(raw_text)
        logger.info("✅ JSON successfully parsed in sanitize_json")
        logger.debug(f"📦 Parsed JSON:\n{json.dumps(parsed, indent=2)}")
        return parsed

    except Exception as e:
        logger.error(f"❌ Failed to sanitize JSON: {e}")
        logger.debug(f"🚨 Offending Raw Text:\n{raw_text}")
        logger.exception("💥 Traceback in sanitize_json:")
        return {
            "summary": "AI parsing failed.",
            "strengths": [],
            "weaknesses": [],
            "recommendation": "Please retry later.",
            "question_answer": "Not provided"
        }


# --- Main Candidate Chat Chain ---
async def run_candidate_chat(candidate_payload: dict, question: str = None) -> dict:
    """
    Takes candidate data + optional HR question and generates structured AI insights.
    Saves chat to MongoDB.
    """
    try:
        logger.info("▶️ run_candidate_chat START")
        logger.debug(f"📥 Candidate Payload:\n{json.dumps(candidate_payload, indent=2)}")
        logger.debug(f"❓ HR Question: {question}")

        filled_prompt = candidate_chat_prompt.format(
            candidate_data=candidate_payload,
            question=question or "No question asked."
        )
        logger.debug(f"📝 Filled Prompt Sent to LLM:\n{filled_prompt}")

        raw_response = await generate_response(filled_prompt)
        logger.debug(f"🤖 Raw Response From LLM:\n{raw_response}")

        result = sanitize_json(raw_response)
        logger.debug(f"✅ Final Parsed AI Result:\n{json.dumps(result, indent=2)}")

        # Save chat log for reference
        chat_log = {
            "candidate_id": candidate_payload.get("candidate", {}).get("id"),
            "job_id": candidate_payload.get("job", {}).get("id"),
            "question": question,
            "response": result,
            "meta": {
                "score": candidate_payload.get("score"),
                "raw_prompt": filled_prompt[:1000]
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        logger.debug(f"📝 Chat Log To Be Inserted Into Mongo:\n{json.dumps(chat_log, default=str, indent=2)}")
        chatlogs_collection.insert_one(chat_log)
        logger.info(f"✅ Chat log saved to Mongo (candidate_id={chat_log['candidate_id']}, job_id={chat_log['job_id']})")

        logger.info("🎯 run_candidate_chat END")
        return result

    except Exception as e:
        logger.error(f"❌ Error in run_candidate_chat: {str(e)}")
        logger.exception("💥 Traceback in run_candidate_chat:")
        return {
            "summary": "AI analysis failed.",
            "strengths": [],
            "weaknesses": [],
            "recommendation": "Please retry later.",
            "question_answer": "No answer due to error."
        }
