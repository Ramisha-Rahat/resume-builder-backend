import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def call_gemini(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        if response and hasattr(response, "text") and response.text:
            return response.text.strip()
        return "No feedback available. Gemini returned an empty response."
    except Exception as e:
        return f"Error: {str(e)}"

def resume_feedback_prompt(resume_text: str) -> str:
    return f"""
You are an expert resume reviewer and ATS consultant.

Analyze the following resume text and provide a detailed professional evaluation including:
1. Key missing sections (e.g., Experience, Skills, Education, Contact Info).
2. An assessment of ATS-friendliness (formatting, structure, keywords).
3. Structural or formatting issues (layout, length, readability).
4. Language or content issues (clarity, redundancy, tone).
5. Your top 5 actionable suggestions to improve the resume's quality and impact.

Resume Text:
\"\"\"
{resume_text}
\"\"\"
"""

# Test resume
resume = """
John Doe
Email: john.doe@example.com | Phone: 123-456-7890
Summary: Experienced software engineer with 5 years in backend development.
Experience: Senior Developer at XYZ Corp. (2018-2022)
Skills: Python, Flask, SQL, Docker
Education: BSc in Computer Science from ABC University
"""

# Generate prompt and call Gemini
prompt = resume_feedback_prompt(resume)
feedback = call_gemini(prompt)
print("\nGemini Feedback:\n")
print(feedback)


# @app.route("/analyze/resume", methods=["POST"])
# def analyze_resume():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files['file']
#     file_path = os.path.join(UPLOAD_DIR, file.filename)
#     file.save(file_path)

#     try:
#         text = extract_resume_text(file_path)
#         ats_score = get_ats_score(text)
#         section_presence = {
#             "contact_info": "email" in text.lower(),
#             "education": "education" in text.lower(),
#             "experience": "experience" in text.lower(),
#             "skills": "skills" in text.lower(),
#             "projects": "project" in text.lower()
#         }

#         return jsonify({
#             "ats_score": ats_score,
#             "section_presence": section_presence
#         })
#     except Exception as e:
#         print("Analysis error:", str(e))
#         return jsonify({"error": "Failed to analyze resume"}), 500