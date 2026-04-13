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
    return parsed_output