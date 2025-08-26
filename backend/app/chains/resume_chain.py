# app/chains/resume_chain.py

from app.services.llm import ask_llm

def resume_chain(resume_text: str) -> dict:
    """
    Extract structured info from a resume using LLM.
    """
    prompt = f"""
    Extract the following from the resume text:
    - Name
    - Email
    - Phone
    - Skills
    - Years of Experience
    - Education
    Resume Text:
    {resume_text}
    """

    response = ask_llm(prompt)
    return {"parsed_resume": response}
