from flask import Flask, request, jsonify
import fitz
import os  
import docx

from flask_cors import CORS
from gemini import (
    generate_summary_prompt,
    generate_experience_bullets_prompt,
    generate_project_summary_prompt,
    extract_technologies_prompt,
    generate_education_summary_prompt,
    generate_complete_resume_prompt,
    resume_feedback_prompt,
    call_gemini
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)

@app.route("/generate/summary", methods=["POST"])
def generate_summary():
    data = request.json
    prompt = generate_summary_prompt(data)
    result = call_gemini(prompt)
    return jsonify({"summary": result})

@app.route("/generate/experience", methods=["POST"])
def generate_experience():
    data = request.json
    prompt = generate_experience_bullets_prompt(data['text'])
    result = call_gemini(prompt)
    bullets = [line.strip("-• ").strip() for line in result.split("\n") if line.strip()]
    return jsonify({"experience_bullets": bullets})

@app.route("/generate/projects", methods=["POST"])
def generate_projects():
    data = request.json
    prompt = generate_project_summary_prompt(data['text'])
    result = call_gemini(prompt)
    return jsonify({"project_summary": result})

@app.route("/generate/technologies", methods=["POST"])
def generate_technologies():
    data = request.json
    prompt = extract_technologies_prompt(data['text'])
    result = call_gemini(prompt)
    technologies = [tech.strip() for tech in result.split(",") if tech.strip()]
    return jsonify({"technologies": technologies})

@app.route("/generate/education", methods=["POST"])
def generate_education():
    data = request.json
    prompt = generate_education_summary_prompt(data['text'])
    result = call_gemini(prompt)
    return jsonify({"education": result})

@app.route("/generate/resume", methods=["POST"])
def generate_resume():
    data = request.json
    prompt = generate_complete_resume_prompt(data)
    result = call_gemini(prompt)
    return jsonify({"resume_text": result})

@app.route("/generate/custom", methods=["POST"])
def generate_custom():
    data = request.json
    prompt = data.get("prompt", "")
    result = call_gemini(prompt)
    return jsonify({"result": result})

def extract_resume_text(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        doc = fitz.open(file_path)
        return "".join([page.get_text() for page in doc])
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        raise ValueError("Unsupported file type")

def get_ats_score(text: str) -> dict:
    text_lower = text.lower()
    score = 0
    max_score = 100
    breakdown = {}

    weights = {
        "contact_info": 10,
        "summary": 10,
        "experience": 25,
        "education": 15,
        "skills": 15,
        "projects": 10,
        "keywords": 10,
        "formatting": 5
    }

    breakdown["contact_info"] = "email" in text_lower or "phone" in text_lower
    breakdown["summary"] = "summary" in text_lower or "objective" in text_lower
    breakdown["experience"] = "experience" in text_lower
    breakdown["education"] = "education" in text_lower
    breakdown["skills"] = "skills" in text_lower
    breakdown["projects"] = "project" in text_lower

    breakdown["keywords"] = any(word in text_lower for word in [
        "developed", "implemented", "designed", "managed", "created"
    ])
    breakdown["formatting"] = "•" in text or "-" in text or "●" in text

    for section, present in breakdown.items():
        if present:
            score += weights[section]

    score = min(score, max_score)

    return {
        "score": score,
      # "breakdown": breakdown
    }

@app.route("/analyze/resume", methods=["POST"])
def analyze_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(file_path)

    try:
        text = extract_resume_text(file_path)
        ats_score = get_ats_score(text)

        # Just return the score (no breakdown)
        return jsonify({
            "ats_score": ats_score
        })

    except Exception as e:
        print("Analysis error:", str(e))
        return jsonify({"error": "Failed to analyze resume"}), 500


@app.route("/feedback/resume", methods=["POST"])
def get_resume_feedback():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(file_path)

    try:
        resume_text = extract_resume_text(file_path)[:6000]
        prompt = resume_feedback_prompt(resume_text)
        feedback = call_gemini(prompt)

        return jsonify({
            "feedback": feedback.strip()
        })

    except Exception as e:
        print("AI Feedback Error:", str(e))
        return jsonify({"error": "Failed to generate AI feedback"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="192.168.26.182", port=5000)

