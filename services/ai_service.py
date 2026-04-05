import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
model = "meta-llama/llama-4-scout-17b-16e-instruct"

def analyze_resume(content, field):
    """Returns a structured analysis instead of just a block of text."""
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a senior recruiter for {field} roles. Help analyze a resume using the industry standards for your field, look out for relevant skills, technology and experience in your field and return a JSON object with keys: 'score' (0-100), 'strengths' (list), and 'weaknesses' (list). Please make the strengths and weaknesses specific and concise. If the resume is not in anyway relevant to the field, do not attempt to placate or hallucinate, rate the score low and point out all the things that would be expected of a resume for that particular field"},
            {"role": "user", "content": f"Analyze this resume for a {field} position. Focus on technical depth and industry-specific impact.\n\nResume Content: {content}"}
        ],
        response_format={"type": "json_object"}
    )
    return completion.choices[0].message.content

def tailor_resume(resume, job_description):
    """Standard text response for generating the updated resume content."""
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Rewrite this resume to match the job description. Do not add conversational filler."},
            {"role": "user", "content": f"Resume: {resume}\nJob: {job_description}"}
        ]
    )
    return completion.choices[0].message.content


def correct_resume(resume, job_description):
    """Standard text response for generating the updated resume content."""
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a professional HR recruiter. Analyze the resume and return a corrected version. Do not add conversational filler"},
            {"role": "user", "content": f"Resume: {resume}\nJob: {job_description}"}
        ]
    )
    return completion.choices[0].message.content

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

