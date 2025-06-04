import ollama
import streamlit as st

def ats_review_and_improve(resume_text: str, job_text: str) -> str:
    prompt = f"""
You are an ATS (Applicant Tracking System) optimization assistant.

Given the following:
- Candidate Resume
- Job Description

Perform the following:
1. Analyze how well the resume matches the job
2. Identify missing or weak skills, keywords, or phrases
3. Suggest concrete improvements to the resume to increase its match score
4. Give a final ATS match score out of 100

Resume:
\"\"\"
{resume_text}
\"\"\"

Job Description:
\"\"\"
{job_text}
\"\"\"

Output your suggestions clearly.
"""

    placeholder = st.empty()
    output = ""

    try:
        response = ollama.chat(
            model='mistral:instruct',
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in response:
            content = chunk['message']['content']
            output += content
            placeholder.markdown(output.strip()) 

    except Exception as e:
        placeholder.error(f"LLM Error: {e}")
        return f"Error: {e}"

    return output  
