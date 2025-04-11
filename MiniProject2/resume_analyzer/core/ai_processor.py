# resume_analyzer/core/ai_processor.py
import spacy
from PyPDF2 import PdfReader
import docx
from io import BytesIO
from spacy.matcher import PhraseMatcher


def load_nlp():
    try:
        return spacy.load('en_core_web_md')
    except OSError:
        return spacy.load('en_core_web_sm')


def extract_text(file_bytes, file_name):
    print(f"Extracting text from file, bytes length: {len(file_bytes)}")
    if not file_bytes:
        raise ValueError("File bytes are empty")
    print(f"File name: {file_name}")
    if file_name.endswith('.pdf'):
        stream = BytesIO(file_bytes)
        stream.seek(0)
        reader = PdfReader(stream)
        text = ''.join([page.extract_text() or '' for page in reader.pages])
    elif file_name.endswith('.docx'):
        doc = docx.Document(BytesIO(file_bytes))
        text = '\n'.join([para.text for para in doc.paragraphs])
    else:
        raise ValueError(f"Unsupported file type: {file_name}")
    print(f"Extracted text length: {len(text)}")
    return text


def analyze_resume(resume_text, skills_required=None):
    nlp = load_nlp()
    doc = nlp(resume_text)
    word_count = len(doc)
    line_count = len(resume_text.split('\n'))

    feedback = {
        'skills': [],
        'formatting': line_count > 5,
        'word_count': word_count,
        'suggestions': []
    }

    if not skills_required or 'skills' not in skills_required:
        feedback['score'] = round(min(word_count / 10, 50) * 0.7 + (20 if feedback['formatting'] else 0) * 0.3, 2)
        feedback['suggestions'].append("Provide a job listing with required skills for a detailed analysis.")
        print(f"No skills required provided. Default score: {feedback['score']}")
        return feedback

    # Extract skills from resume
    matcher = PhraseMatcher(nlp.vocab)
    job_skills = skills_required['skills']
    matcher.add("JOB_SKILLS", [nlp(skill) for skill in job_skills])
    matches = matcher(doc)
    resume_skills = list(set([doc[start:end].text for match_id, start, end in matches]))
    print(f"Extracted skills from resume: {resume_skills}")

    # Calculate skill density
    skill_density = len(resume_skills) / word_count if word_count > 0 else 0
    feedback['skills'] = resume_skills
    feedback['skill_density'] = round(skill_density * 100, 2)

    # Scoring
    formatting_score = 20 if feedback['formatting'] else 0
    length_score = min(max((word_count - 100) / 10, 0), 20)
    skill_match = len(set(resume_skills) & set(job_skills)) / len(job_skills) * 100 if job_skills else 0
    feedback['score'] = round(skill_match * 0.7 + formatting_score * 0.2 + length_score * 0.1, 2)
    missing_skills = set(job_skills) - set(resume_skills)
    feedback['missing_skills'] = list(missing_skills)
    print(f"Skill match: {skill_match}, Final score: {feedback['score']}")

    # Suggestions
    if len(resume_skills) < len(job_skills) * 0.5:
        feedback['suggestions'].append("Add more job-specific skills to improve your match.")
    if missing_skills:
        feedback['suggestions'].append(f"Consider including: {', '.join(missing_skills)}")
    if word_count < 200:
        feedback['suggestions'].append("Expand your resume with more details (e.g., achievements, projects).")
    if skill_density < 0.02:
        feedback['suggestions'].append("Increase keyword usage to highlight your expertise.")

    return feedback