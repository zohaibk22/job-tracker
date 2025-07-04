from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
import json

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

def classify_email(email:dict) -> dict:
    print("IN CLASSIFY EMAIL CONTENT 🚀")
    subject = email.get("subject", "")
    body = email.get("body", "")[:1000]

    system_msg = SystemMessage(content=(
        "You're an email assistant. Determine whether an email is about a job application, whether it is a new submission, or a status update from a previous submission. It can be the submission itself. As long as it is a job application I submitted. Do not consider emails that are about job offers, new positions openings or any other job-related topics. Focus only on the job application status and submissions.\n\n"
        "Respond with JSON like: {\"is_job_application\": true/false, \"reason\": \"...\", \"status\": Applied/Interview-requested/Rejected}. For the  \"status\" key value pair, assign it \"applied\" if the email is about a new job application submission, and then \"interview-requested\" or \"rejected\" if the email is about a previous job application I submitted in the past. Remember to only use \"Applied\",\"Interview-request\", or \"Rejected \" for the status field and no other values! Please account for assessment requests, next step interviews, or offer updates under interview request. Do not add any other text"
    ))


    user_msg = HumanMessage(content=f"Subject: {subject}\n\nBody: {body}")
    
    response = llm.invoke([system_msg, user_msg])
    print(f"Response: {response.content} --------------------------")
    try:
        result = json.loads(response.content)
      
    except Exception as e:
        result = {"is_job_application": False, "reason": "Could not parse response", "status": "Unknown"}


    return result