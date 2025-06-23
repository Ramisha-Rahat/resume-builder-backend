import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Core Gemini call
def call_gemini(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"


def resume_feedback_prompt(text: str) -> str:
    return f"""
Analyze the following resume text and provide 5-6 concise, clear bullet points of feedback to improve the resume. 
Focus on areas like formatting, clarity, missing sections, weak language, or ATS optimization.

Only return the feedback points in markdown bullet format.

Resume:
{text}
"""


# Prompts
def generate_summary_prompt(data: dict) -> str:
    name = data.get("name", "User")
    role = data.get("role", "Software Developer")
    skills = ", ".join([skill.get("name", "") for skill in data.get("skills", [])])
    experience = data.get("experience", "")
    return f"""
Generate a professional resume summary for {name}, targeting the role of {role}.
Skills: {skills}.
Experience summary: {experience}.
Keep it concise and impactful (3-4 lines).
"""

def generate_experience_bullets_prompt(text: str) -> str:
    return f"""
Generate 3-5 concise, professional resume bullet points based on the following work experience description.
Do not include placeholders like [quantifiable result] or [metrics]. Just focus on clearly explaining the candidate’s work and impact:

{text}
"""

def generate_project_summary_prompt(text: str) -> str:
    return f"Summarize this project for a resume, highlighting technologies and outcomes: {text}"

def extract_technologies_prompt(text: str) -> str:
    return f"Extract and list all technologies, tools, and programming languages mentioned in this text: {text}"

def generate_education_summary_prompt(text: str) -> str:
    return f"Create a brief, formal education section summary for a resume based on this: {text}"

def generate_complete_resume_prompt(data: dict) -> str:
    return f"""
Create a professional resume based on the following data:
Name: {data.get("name")}
Title: {data.get("title")}
Email: {data.get("email")}
Phone: {data.get("phone")}
Location: {data.get("location")}
LinkedIn: {data.get("linkedin")}
GitHub: {data.get("github")}
Summary: {data.get("summary")}

Skills:
{', '.join([f"{s.get('category', '')}: {', '.join(s.get('items', []))}" for s in data.get("skills", [])])}

Experience:
{"".join([
    f"{exp.get('company', 'Unknown Company')} - {exp.get('role', 'Unknown Role')} ({exp.get('duration', 'N/A')})\n"
    f"Responsibilities: {', '.join(exp.get('responsibilities', []))}\n"
    f"Technologies: {', '.join(exp.get('technologies', []))}\n\n"
    for exp in data.get('experience', [])
])}

Projects:
{"".join([
    f"{proj.get('title', 'Untitled Project')} - {proj.get('description', '')}\n"
    f"Tech Stack: {', '.join(proj.get('technologies', []))}\n\n"
    for proj in data.get('projects', [])
])}

Education:
{data.get('education', {}).get('degree')} from {data.get('education', {}).get('institution')}
({data.get('education', {}).get('year')}), GPA: {data.get('education', {}).get('gpa')}

Certifications:
{', '.join(data.get('certifications', []))}

Structure the resume with clear sections and formatting.
"""
