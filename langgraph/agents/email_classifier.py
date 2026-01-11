from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
import json
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

def classify_email(email:dict) -> dict:
    subject = email.get("subject", "")
    body = email.get("body", "")[:1000]

    system_msg = SystemMessage(content=(
        "You're an email assistant. Your task is to classify emails related to MY job applications.\n\n"
        
        "INCLUDE:\n"
        "- New job application submissions that I sent\n"
        "- Status updates on previous applications I submitted\n"
        "- The application submission itself\n\n"
        
        "EXCLUDE:\n"
        "- Job offers ads or position openings from recruiters\n"
        "- General job-related topics\n\n"
        
        "RESPONSE FORMAT:\n"
        "Respond with JSON only, no additional text:\n"
        '{{"is_job_application": true/false, "reason": "...", "status": "Applied/Interview-requested/Rejected"}}\n\n'
        
        "STATUS FIELD RULES:\n"
        '- Use "Applied" for new job application submissions\n'
        '- Use "Interview-requested" for:\n'
        "  * Interview invitations\n"
        "  * Assessment requests\n"
        "  * Next step communications\n"
        "  * Offer updates\n"
        '- Use "Rejected" for rejection notifications\n'
        '- Use "Unknown" if is_job_application is false\n'
        f'- ignore emails from {os.getenv("SUMMARY_EMAIL_ADDRESS")}\n'
        '- if status is not clear from the email, set is_job_application to false and status to "Unknown"\n'
        "- No other values are allowed\n\n"
        
        
        "IMPORTANT:\n"
        'If is_job_application is false, set reason to "Email is not about job application" and status to "Unknown"'
    ))


    user_msg = HumanMessage(content=f"Subject: {subject}\n\nBody: {body}")
    
    response = llm.invoke([system_msg, user_msg])
    try:
        content = response.content
        logger.info(f"Response content: {content}")
        
        # Strip markdown code blocks if present
        if isinstance(content, str) and content.startswith("```"):
            content = content.strip()
            content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        
        if isinstance(content, bytes):
            result = json.loads(content.decode('utf-8'))
        elif isinstance(content, str):
            result = json.loads(content)
        else:
            result = json.loads(str(content))
        
    except Exception as e:
        logger.error(f"Error parsing JSON response: {e}")
        result = {"is_job_application": False, "reason": "Could not parse response", "status": "Unknown"}


    return result