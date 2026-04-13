'''
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StructuredOutputParser, ResponseSchema
import os

groq_api_key=os.getenv("GROQ_API_KEY")
# LLM
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama3-70b-8192",
    temperature=0.3
)

# Define output schema
schemas = [
    ResponseSchema(name="action_items", description="List of action items with assignee and deadline"),
    ResponseSchema(name="decisions", description="List of decisions made"),
    ResponseSchema(name="questions", description="Unresolved questions"),
    ResponseSchema(name="topics", description="Topics discussed")
]

parser = StructuredOutputParser.from_response_schemas(schemas)

# Prompt
template = """
Extract structured meeting insights.

{format_instructions}

Transcript:
{transcript}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["transcript"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Function
def extract_insights(transcript_text):
    formatted_prompt = prompt.format(transcript=transcript_text)
    
    response = llm.invoke(formatted_prompt)
    
    parsed_output = parser.parse(response.content)
    print(parsed_output)
    return parsed_output'''
from groq import Groq
import os
import json
import re
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

# -------------------------
# Load ENV
# -------------------------
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("Groq connected")


# -------------------------
# Pydantic Schemas
# -------------------------
class ActionItem(BaseModel):
    task: str
    assignee: str
    deadline: str


class MeetingInsights(BaseModel):
    summary: str = ""
    action_items: List[ActionItem] = []
    decisions: List[str] = []
    questions: List[str] = []
    topics: List[str] = []


# -------------------------
# Extract JSON safely
# -------------------------
def extract_json(text):
    try:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print("JSON parse error:", e)
    return None


# -------------------------
# Main Function
# -------------------------
def extract_insights(transcript_text):
    prompt = f"""
You are an AI system that extracts structured meeting intelligence.

Extract the following in STRICT JSON format:

{{
  "summary": "Concise summary of the meeting",
  "action_items": [
    {{
      "task": "Clearly defined task",
      "assignee": "Person responsible",
      "deadline": "Deadline if mentioned, else empty string"
    }}
  ],
  "decisions": ["List of decisions made"],
  "questions": ["Questions that were NOT answered or deferred"],
  "topics": ["Key discussion topics"]
}}

Rules:
- Return ONLY valid JSON
- Do NOT include explanations or markdown
- Do NOT include any text outside JSON
- If information is missing, return empty string or empty list
- Ensure JSON is syntactically valid

Action Item Rules:
- Include ONLY tasks explicitly assigned to a person
- The assignee MUST be clearly mentioned in the transcript
- Do NOT convert decisions into action items
- Do NOT infer or assume tasks
- Each action item must be actionable and specific

Decision Rules:
- Include only finalized agreements or conclusions
- Do NOT include suggestions or discussions as decisions

Question Rules:
- Include ONLY unanswered or deferred questions in "open_questions"

Transcript:
{transcript_text}
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.05
        )

        content = response.choices[0].message.content

        # -------------------------
        # Step 1: Extract JSON
        # -------------------------
        parsed = extract_json(content)

        # -------------------------
        # Step 2: Validate using Pydantic
        # -------------------------
        if parsed:
            try:
                validated = MeetingInsights(**parsed)
                return validated.dict()
            except Exception as e:
                print("Validation error:", e)

        # -------------------------
        # Step 3: Retry once (optional but strong)
        # -------------------------
        print("Retrying LLM...")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        content = response.choices[0].message.content
        parsed = extract_json(content)

        if parsed:
            try:
                validated = MeetingInsights(**parsed)
                return validated.dict()
            except Exception as e:
                print("Retry validation error:", e)

        # -------------------------
        # Step 4: Final fallback
        # -------------------------
        return {
            "summary": "",
            "action_items": [],
            "decisions": [],
            "questions": [],
            "topics": [],
            "raw_output": content
        }

    except Exception as e:
        print("LLM error:", e)
        return {
            "summary": "",
            "action_items": [],
            "decisions": [],
            "questions": [],
            "topics": [],
            "error": str(e)
        }