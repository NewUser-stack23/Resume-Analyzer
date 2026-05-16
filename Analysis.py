import streamlit as st  # type: ignore
import docx  # type: ignore
import fitz  # PyMuPDF # type: ignore
import re  # type: ignore
import matplotlib.pyplot as plt  # type: ignore


st.set_page_config(page_title="Smart Resume Analyzer", layout="centered")
st.title("📄 Smart Resume Analyzer")
st.markdown("Analyze your resume's match with job descriptions, view skill coverage, and get job role insights.")


uploaded_file = st.file_uploader("Upload your resume (.pdf or .docx)", type=["pdf", "docx"])
job_description = st.text_area("Paste the job description here:")
custom_skills_input = st.text_input("Enter required skills (comma-separated):", placeholder="e.g. Python, SQL, Teamwork")

def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_keywords(text):
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = set([
        "the", "and", "to", "of", "in", "for", "on", "with", "a", "an", "is",
        "at", "by", "this", "that", "are", "as", "be", "from", "or", "will", "can"
    ])
    return [word for word in words if word not in stopwords and len(word) > 2]

def recommend_skills(job_keywords, resume_keywords):
    return list(set(job_keywords) - set(resume_keywords))

def predict_job_role(resume_text):
    role_keywords = {
        "Software Engineer": ["python", "java", "c++", "git", "scalable", "algorithm", "backend", "frontend", "full stack", "object oriented"],
        "Data Scientist": ["machine learning", "data", "pandas", "statistics", "model", "numpy", "regression", "visualization", "jupyter"],
        "Frontend Developer": ["react", "javascript", "html", "css", "ui", "ux", "tailwind", "next.js", "component", "design"],
        "Backend Developer": ["node", "django", "api", "server", "database", "sql", "rest", "flask", "load balancing"],
        "DevOps Engineer": ["docker", "kubernetes", "ci/cd", "aws", "infrastructure", "pipeline", "terraform", "ansible", "monitoring"],
        "QA Engineer": ["test", "automation", "selenium", "quality", "junit", "bug", "manual testing", "testcase"],
        "Product Manager": ["stakeholder", "roadmap", "agile", "scrum", "vision", "strategy", "kpi", "cross-functional"],
        "UI/UX Designer": ["figma", "wireframe", "prototype", "user research", "accessibility", "visual design"]
    }

    resume_text_lower = resume_text.lower()
    scores = {}

    for role, keywords in role_keywords.items():
        matches = sum(1 for kw in keywords if kw in resume_text_lower)
        scores[role] = matches

    predicted_role = max(scores, key=scores.get)
    confidence = (scores[predicted_role] / len(role_keywords[predicted_role])) * 100

    return predicted_role, confidence


if uploaded_file and job_description:
    # Extract resume text
    resume_text = extract_text_from_pdf(uploaded_file) if uploaded_file.name.endswith(".pdf") else extract_text_from_docx(uploaded_file)

    # Extract keywords
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)

    # Job keyword match
    matched_keywords = list(set(resume_keywords) & set(job_keywords))
    missing_keywords = list(set(job_keywords) - set(resume_keywords))
    job_match_percentage = (len(matched_keywords) / len(job_keywords)) * 100 if job_keywords else 0

    # Custom Skills Match
    user_skills = [skill.strip() for skill in custom_skills_input.split(",") if skill.strip()]
    resume_lower = resume_text.lower()
    matched_user_skills = [skill for skill in user_skills if skill.lower() in resume_lower]
    missing_user_skills = list(set(user_skills) - set(matched_user_skills))
    skill_match_percentage = (len(matched_user_skills) / len(user_skills)) * 100 if user_skills else 0

    # Final Score
    if job_keywords and user_skills:
        final_match_score = (job_match_percentage + skill_match_percentage) / 2
    elif job_keywords:
        final_match_score = job_match_percentage
    elif user_skills:
        final_match_score = skill_match_percentage
    else:
        final_match_score = 0

    # Recommend missing skills
    recommended_skills = recommend_skills(job_keywords, resume_keywords)

    # Predict job role
    predicted_role, confidence = predict_job_role(resume_text)

    
    st.subheader("📊 Match Analysis")
    st.write(f"**Job Description Match Score:** {job_match_percentage:.2f}%")                     
    st.write(f"**Custom Skill Match Score:** {skill_match_percentage:.2f}%")
    st.write(f"🎯 **Final Match Score:** `{final_match_score:.2f}%`")

    st.write(f"**Matched Job Keywords:** {', '.join(matched_keywords) or 'None'}")
    st.write(f"**Missing Job Keywords:** {', '.join(missing_keywords) or 'None'}")

    st.write(f"**Matched Required Skills:** {', '.join(matched_user_skills) or 'None'}")
    st.write(f"**Missing Required Skills:** {', '.join(missing_user_skills) or 'None'}")

    if recommended_skills:
        st.subheader("🧠 Recommended Skills Based on Job Description")
        st.write(", ".join(recommended_skills))
    else:
        st.write("✅ No missing keywords from the job description!")

    st.subheader("🎯 Predicted Job Role")
    st.write(f"Likely Role: **{predicted_role}** with **{confidence:.1f}% confidence**")

    
    st.subheader("📈 Match Score Chart")
    st.bar_chart({
        "Matched Job Keywords": [len(matched_keywords)],
        "Total Job Keywords": [len(job_keywords)],
        "Matched Required Skills": [len(matched_user_skills)],
        "Total Required Skills": [len(user_skills)]
    })

    st.subheader("🧩 Skill Coverage Pie Chart")
    fig, ax = plt.subplots()
    ax.pie(
        [len(matched_user_skills), len(missing_user_skills)],
        labels=["Matched Skills", "Missing Skills"],
        colors=["#4CAF50", "#FF7043"],
        autopct="%1.1f%%", startangle=90
    )
    ax.axis('equal')
    st.pyplot(fig)

else:
    st.info("Upload your resume and enter the job description and required skills to begin analysis.")
