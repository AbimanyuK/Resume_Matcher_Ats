import streamlit as st
import os
import uuid
import numpy as np
from data_extraction import extract_text_from_file
from data_embedding import get_text_embedding
from faiss_search import build_faiss_index, search_index
from ats_llm import ats_review_and_improve

st.set_page_config(page_title="AI Job Match & ATS Review", layout="centered")
st.title("AI Resume Matcher + ATS Review")
st.write("Upload your resume and match it to job descriptions semantically. Get live suggestions from a local LLM.")

resume_file = st.file_uploader("Upload your resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

jd_files = st.file_uploader(
    "Upload one or more Job Descriptions (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if jd_files:
    max_val = len(jd_files)
    top_k = st.slider("Number of top job matches", min_value=1, max_value=max_val, value=max_val)
else:
    top_k = None
    
if st.button("Match & Analyze"):
    if not resume_file or not jd_files:
        st.warning("Please upload a resume and select at least one job description.")
    else:
        os.makedirs("temp", exist_ok=True)

        resume_path = os.path.join("temp", resume_file.name)
        with open(resume_path, "wb") as f:
            f.write(resume_file.read())

        st.info("Extracting and embedding resume...")
        resume_text = extract_text_from_file(resume_path)
        resume_embedding = get_text_embedding(resume_text)

        job_texts = []
        job_embeddings = []
        job_filenames = []

        for file in jd_files:
            unique_name = f"{uuid.uuid4().hex}_{file.name}"
            jd_path = os.path.join("temp", unique_name)
            with open(jd_path, "wb") as f:
                f.write(file.read())

            job_text = extract_text_from_file(jd_path)
            if job_text and job_text.strip():
                embedding = get_text_embedding(job_text)
                if np.any(embedding):
                    if job_text.strip() not in job_texts:  
                        job_texts.append(job_text)
                        job_filenames.append(file.name)
                        job_embeddings.append(embedding)
                    else:
                        st.warning(f"Skipping duplicate content: {file.name}")
                else:
                    st.warning(f"Skipping {file.name}: empty or invalid embedding.")
            else:
                st.warning(f"Skipping {file.name}: could not extract readable text.")

        if not job_embeddings:
            st.error("No valid job descriptions found.")
        else:
            top_k = min(top_k, len(job_embeddings))
            st.success(f"Loaded {len(job_embeddings)} valid job descriptions.")

            index = build_faiss_index(job_embeddings)
            scores, indices = search_index(index, resume_embedding, top_k=top_k)

            st.markdown("---")
            st.subheader("Top Job Matches + ATS Suggestions")

            for i, idx in enumerate(indices):
                job_file = job_filenames[idx]
                job_text = job_texts[idx]

                st.markdown(f"**{i+1}. {job_file}** - Similarity Score: `{scores[i]*100:.2f}`")
                with st.spinner("Running ATS review..."):
                    ats_review_and_improve(resume_text, job_text)
                st.markdown("---")

    