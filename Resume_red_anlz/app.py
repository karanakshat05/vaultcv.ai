import streamlit as st
import re

from analyzer.analyser import extract_sections, calculate_ats_score

# Title
st.title("📄 AI Resume Analyzer")

# Upload Resume
uploaded_file = st.file_uploader("Upload ur resume", type=["pdf"])

# Select Experience Level
experience_level = st.selectbox(
    "Select your experience level:",
    ["fresher", "mid", "advanced"],
    index=0
)

# (Optional) Buzzwords list (you can customize later)
buzzword_list = ["leadership", "teamwork", "communication", "initiative", "critical thinking"]

if uploaded_file is not None:
    # read the uploaded file
    file_bytes = uploaded_file.read()

    #now lets decode the bytes into string
    text = file_bytes.decode("utf-8", errors="ignore")
    # now we can extract the the data
    extracted_data = extract_sections(text)

    # Calculate ATS Score
    score = calculate_ats_score(
        extracted_data,
        experience_level=experience_level,
        buzzwords=buzzword_list
    )

    # Display Result
    st.success(f"✅ Your ATS Score: {score} / 100")

    # Optionally show extracted sections
    with st.expander("See extracted resume sections"):
        st.write(extracted_data)
else:
    st.info("👆 Please upload your resume to start analysis.")
