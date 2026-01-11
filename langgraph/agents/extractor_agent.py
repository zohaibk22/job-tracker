import json
from langchain_openai import ChatOpenAI

from langchain.schema import SystemMessage, HumanMessage

llm = ChatOpenAI(model="gpt-4o", temperature=0.0)



def extract_email_content(email: dict) -> dict:
    subject = email.get('subject', '')
    body = email.get('body', '')[:2000]  # Limit to first 2000 characters
    date = email.get('date', '')


    
    system_msg = SystemMessage(content=(
        """
            You are an AI assistant that extracts structured job application details from emails.

            TASK:
            Extract the following information and return ONLY valid JSON:
            - "company": The company name
            - "job_title": The job position title
            - "submission_date": When the application was submitted

            EXTRACTION RULES:

            Company Name:
            - Search all fields (subject, body, sender) for the company name
            - If not found, return "unknown"

            Job Title:
            - Search all fields  (subject, body, sender) for the job title
            - If not found, return "Software Engineer" as default

            Submission Date:
            - Look for dates explicitly related to application submission
            - Keywords to look for: "submission", "submitted", "applied"
            - If uncertain, use the email's date or current date
            - Format: "full month name day, year" (e.g., "January 1, 2023")

            OUTPUT:
            - Return ONLY valid JSON, no code fences or extra text
            - No markdown formatting or explanations
         """
    ))


    human_message = HumanMessage(content=(
        f"Subject: {subject}\n"
        f"Body: {body}\n"
        f"Date: {date}\n"
    ))

    response = llm.invoke([system_msg, human_message])
    content = response.content.strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {"company": "unknown", "job_title": "Software Engineer", "submission_date": date, }

    return data
