#loading all the libraries and modules
import spacy
import re
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

#loading the spaCy's small ENglish model
nlp = spacy.load("en_core_web_sm")

# now define all skillset with domain
SKILLS_BY_DOMAIN = {
    "tech": {
        "python", "java", "c++", "javascript", "react", "node", "git", "docker",
        "aws", "azure", "ml", "ai", "deep learning", "tensorflow", "nlp"
    },

    "mechanical": {"solidworks", "autocad", "thermodynamics", "fluids", "cad", "mechanics", "mechatronics"},
    "civil": {"staad", "autocad", "structural", "geotech", "surveying", "concrete", "urban planning"},
    "electrical": {"circuits", "power systems", "switchgear", "transformer", "vlsi", "signal processing"},
    "chemical": {"reactor design", "mass transfer", "thermodynamics", "process control", "hysys"},
    "production": {"lean manufacturing", "tpm", "supply chain", "industrial engineering", "quality control"},
    "metallurgical": {"materials", "heat treatment", "alloys", "phase diagram", "failure analysis"},
    "mining": {"mineral processing", "rock mechanics", "surveying", "mine planning", "blasting"},

    "management": {
        "leadership", "strategy", "finance", "communication", "negotiation",
        "project management", "operations", "marketing", "business analysis"
    }

}


def extract_sections(text, domain="tech"):
    """
    Extracting skills, education, and experience from resume text.
    here we are using keyword matching and light NLP.
    """
    education, experience, skills = [], [], set()
    sentences = sent_tokenize(text.lower())
    domain_skills = SKILLS_BY_DOMAIN.get(domain, set())

    for sentence in sentences:
        if any(keyword in sentence for keyword in ['bachelor', 'master', 'university', 'degree', 'school']):
            education.append(sentence)
        if any(keyword in sentence for keyword in ['experience', 'worked', 'intern', 'project']):
            experience.append(sentence)
        for skill in domain_skills:
            if skill in sentence:
                skills.add(skill)

    return {
        "education": education,
        "experience": experience,
        "skills": list(skills)
    }


def match_job_description(resume_text, jd_text):
    """
    Uses TF-IDF and cosine similarity to find textual match between resume and job description.
    """
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, jd_text])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(score * 100, 2)


def calculate_ats_score(extracted_data, experience_level="fresher", buzzwords=None):
    domain_weights = {
        "fresher": (0.6, 0.25, 0.05, 0.1),  # focus on skills + education
        "mid": (0.45, 0.2, 0.25, 0.1),
        "advanced": (0.3, 0.1, 0.5, 0.1)  # experience heavy
    }

    skill_wt, edu_wt, exp_wt, bonus_wt = domain_weights.get(experience_level, (0.4, 0.1, 0.4, 0.1))
    max_score = 100
    score = 0

    # Skills
    resume_skills = set(extracted_data.get("skills", []))
    skill_score = len(resume_skills) / 10 * skill_wt * max_score  # normalize with base value
    score += skill_score

    # Education
    edu_score = min(len(extracted_data.get("education", [])) / 2, 1) * edu_wt * max_score
    score += edu_score

    # Experience
    experiences = extracted_data.get("experience", [])
    exp_score = min(len(experiences) / 5, 1) * exp_wt * max_score
    score += exp_score

    # Bonus: internships, bullet quality, buzzword match
    bonus = 0
    internships = [e for e in experiences if "intern" in e.lower()]
    if experience_level == "fresher" and internships:
        bonus += 5  # internship bonus

    # Bullet quality
    bullet_points = sum(1 for exp in experiences if "-" in exp or "•" in exp)
    if bullet_points >= len(experiences) * 0.8:  # high-quality formatting
        bonus += 5

    # Buzzword match
    if buzzwords:
        text = " ".join(resume_skills | set(" ".join(experiences).split()))
        buzz_hits = sum(1 for word in buzzwords if word.lower() in text.lower())
        bonus += min(buzz_hits, 5)

    score += min(bonus, bonus_wt * max_score)
    return round(min(score, max_score), 2)


def analyse_resume(resume_text, job_description, domain="tech"):
    """
    Performs full resume analysis:
    - Extract sections
    - Match with job description
    - Compute ATS score
    """
    extracted_data = extract_sections(resume_text, domain)
    match_score = match_job_description(resume_text, job_description)
    ats_score = calculate_ats_score(extracted_data, job_description, domain)

    return {
        "extracted_data": extracted_data,
        "match_score": match_score,
        "ats_score": ats_score,
        "domain": domain
    }


def detect_domain_from_jd(jd_text):
    jd_text = jd_text.lower()
    for domain, skills in SKILLS_BY_DOMAIN.items():
        if any(skill in jd_text for skill in skills):
            return domain
    return "tech"  # default fallback



