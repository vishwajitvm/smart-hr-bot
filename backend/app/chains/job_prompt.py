# app/chains/job_prompt.py
from langchain.prompts import ChatPromptTemplate

# Prompt template for structured job generation
job_prompt = ChatPromptTemplate.from_template("""
You are an HR assistant helping to create structured job postings.

Job Title: {title}

Return the output strictly as a valid JSON object with the following keys:
- title
- department
- location
- workMode
- type
- experience
- openings
- salary
- description (HTML format <p>…</p>)
- responsibilities (HTML format <ul><li>…</li></ul>)
- requirements (HTML format <ul><li>…</li></ul>)
- benefits (HTML format <ul><li>…</li></ul>)
- hiringManager

Guidelines:
- Keep responses concise, professional, and industry-appropriate.
- Avoid adding company-specific names unless provided.
- Do NOT include commentary outside JSON.
""")
