import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables from the .env configuration layout
load_dotenv()

def _call_openrouter(prompt: str) -> str:
    """
    Common internal service method to execute standard HTTP POST requests 
    towards the OpenRouter completion interface using the Llama-3 model instance.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    model = "meta-llama/llama-3-8b-instruct"
    
    try:
        response = requests.post(
            url=url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        data = response.json()
        print("OpenRouter response snapshot:", data)
        
        if "error" in data:
            return f"AI Service Error: {data['error'].get('message', 'Unknown error')}"
            
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"An error occurred while calling AI service: {str(e)}"


def generate_student_comment(transcript_data: list, student_name: str) -> str:
    """
    Generates an AI-powered analytical performance evaluation text summary 
    for a student based on their processed transcript records. Entirely in English.
    """
    if not transcript_data:
        return "No grade data found for this student."

    # Parse and compile the collection of raw academic listings into a narrative context block
    lesson_summary = ""
    for item in transcript_data:
        lesson_summary += (
            f"- {item['lesson_name']} ({item['grade_type']}): "
            f"Grade: {item['grade_value']}, "
            f"Absenteeism: {item.get('absenteeism_count', item.get('absenteeism', 0))}, "
            f"Status: {item['status']}\n"
        )

    # Contextual prompt construction enforcing strict English localization constraints
    prompt = f"""You are a student academic advisor. Below are the grades and attendance records for a student named {student_name}.

{lesson_summary}

STRICT RULE: You must write the entire review strictly in English. NEVER use Turkish or any other language.

Based on this data:
1. Evaluate the student's overall academic performance.
2. Identify their strengths and areas that need improvement.
3. Provide short, constructive advice.

Keep your response concise (3-5 sentences max)."""

    return _call_openrouter(prompt)


def generate_student_recommendations(transcript_data: list, student_name: str) -> str:
    """
    Analyzes holistic student academic milestones to automatically produce 
    actionable study planners and remediation strategies for risk mitigation.
    """
    if not transcript_data:
        return "No sufficient academic data found to generate recommendations."

    lesson_summaries = []
    weak_lessons = []
    at_risk_lessons = []

    # Sort through course vectors to categorize core failure or absenteeism signals
    for item in transcript_data:
        lesson_name = item.get("lesson_name", "Unknown Lesson")
        grade_value = item.get("grade_value", 0)
        grade_type = item.get("grade_type", "")
        absenteeism = item.get("absenteeism", 0)
        status = item.get("status", "Unknown")

        lesson_summaries.append(
            f"- {lesson_name} ({grade_type}): Grade={grade_value}/100, Status={status}, Attendance={absenteeism} days"
        )

        # Trigger risk flag categorization thresholds safely
        if grade_value < 60:
            weak_lessons.append(lesson_name)
        if absenteeism >= 3:
            at_risk_lessons.append(lesson_name)

    lessons_block = "\n".join(lesson_summaries)
    weak_block = ", ".join(weak_lessons) if weak_lessons else "None"
    at_risk_block = ", ".join(at_risk_lessons) if at_risk_lessons else "None"

    prompt = f"""You are an experienced academic advisor and education coach.
Below are the current academic records for a student named {student_name}.

=== ACADEMIC STATUS ===
{lessons_block}

=== RISK ANALYSIS ===
Courses at risk of failure (Grade < 60): {weak_block}
Courses at risk of attendance limit (≥3 days): {at_risk_block}

Based on this data, please provide {student_name} with:
1. A brief overall academic evaluation.
2. A step-by-step actionable study plan tailored to their weak courses (at least 2 concrete strategies per course).
3. An action plan for attendance issues, if any.
4. A motivating, realistic closing message.

Respond strictly in English. Use bullet points and clear headings. Length: 250-400 words."""

    return _call_openrouter(prompt)


def parse_natural_language_query(user_query: str) -> dict:
    """
    NLP Translation gateway layer. Evaluates natural language expressions and 
    maps structural properties into deterministic schema filters using strict JSON rules.
    """
    system_instruction = """You are a strict JSON query parser for a student management system.

Your ONLY task is to convert the user's natural language request into a JSON object
that matches ONE of the following schemas. Do NOT add explanations, markdown, or extra text.
Return RAW JSON only.

SUPPORTED ACTIONS:

1. List students sorted by average grade (GPA):
{"action": "list_students", "sort_by": "gpa", "order": "asc" | "desc", "limit": <integer>}

2. Filter students by absenteeism in a specific lesson:
{"action": "filter_absenteeism", "lesson_name": "<string>", "threshold": <integer>, "operator": "gt" | "lt" | "gte" | "lte"}

3. Filter students by grade in a specific lesson:
{"action": "filter_grade", "lesson_name": "<string>", "threshold": <number>, "operator": "gt" | "lt" | "gte" | "lte"}

4. If the request does not match any schema or is unclear:
{"action": "unknown"}

RULES:
- "order" defaults to "desc" if not specified.
- "limit" defaults to 10 if not specified.
- "operator" defaults to "gt" if not specified.
- lesson_name must be extracted exactly as mentioned by the user (e.g., "Deep Learning").
- Output MUST be valid JSON. No comments, no trailing text, no code blocks.
"""

    prompt = f"{system_instruction}\n\nUser request: \"{user_query}\"\n\nJSON output:"
    raw_output = _call_openrouter(prompt)

    try:
        # Sanitize output boundaries and strip markdown code blocks safely if present
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "", 1).strip()

        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict) or "action" not in parsed:
            return {"action": "unknown"}

        return parsed
    except (json.JSONDecodeError, ValueError):
        return {"action": "unknown"}    
    

def generate_chatbot_response(
    user_message: str,
    transcript_data: list,
    student_name: str,
    current_gpa: float  
) -> str:
    """
    Context Injection Chatbot Engine. Pairs real-time transactional transcript snapshots 
    and pre-calculated cumulative metrics with direct user prompts to govern LLM reasoning.
    """
    if not transcript_data:
        return "I couldn't find any academic records associated with your account."

    # Map contextual object hierarchies down into plaintext tokens vectors safely
    context_lines = []
    for item in transcript_data:
        lesson = item.get('lesson_name', 'Unknown Lesson')
        g_type = item.get('grade_type', 'Evaluation')
        g_val = item.get('grade_value', 'N/A')
        status = item.get('status', 'Unknown')
        absenteeism = item.get('absenteeism_count', item.get('absenteeism', 0))
        
        context_lines.append(
            f"- {lesson} ({g_type}): Grade: {g_val}/100, Absenteeism: {absenteeism} days, Status: {status}"
        )
    context_block = "\n".join(context_lines)

    prompt = f"""You are an academic assistant chatbot and personal mentor for a student named {student_name}.
Address the student directly as "you" (e.g., "Your average looks good", "You have passed..."). Do not refer to them as "the student".

STRICT RULES:
1. You are explicitly provided with the student's exact pre-calculated Cumulative GPA (Average Grade) in the records below. Use this exact number ({current_gpa}) when they ask about their GPA, overall grade, or average. Do NOT say you cannot calculate it.
2. Answer based on the academic data provided below. Do NOT invent or hallucinate records that do not exist.
3. If the student asks something completely unrelated to their academic status, courses, or grades, say: "I don't have enough information to answer that."
4. Always respond in English, regardless of the language the student uses.
5. Keep your answer concise (2-4 sentences max).

=== STUDENT ACADEMIC RECORDS ===
- Cumulative GPA (Overall Average Grade): {current_gpa} out of 100
{context_block}
================================

Student's question: {user_message}

Your response:"""

    return _call_openrouter(prompt)