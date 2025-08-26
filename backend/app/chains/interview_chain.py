# app/chains/interview_chain.py

from app.services.llm import ask_llm

def interview_chain(candidate_data: dict) -> dict:
    """
    Run an interview simulation with the LLM.
    candidate_data: { 'name': str, 'skills': list[str], 'experience': str }
    """
    questions = [
        f"Tell me about your experience in {', '.join(candidate_data['skills'])}.",
        "What was the biggest challenge in your previous role?",
        "How do you handle stress during deadlines?",
    ]

    answers = []
    for q in questions:
        response = ask_llm(f"Candidate: {candidate_data['name']}\nQuestion: {q}")
        answers.append({"question": q, "answer": response})

    return {"candidate": candidate_data["name"], "interview": answers}
