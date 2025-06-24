
from dotenv import load_dotenv
import os
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from agents import fetch_today_emails
from agents import classify_email
from agents import extract_email_content
from agents import write_to_sheet
from graph import build_graph




def main():
    load_dotenv()
    # emails = fetch_today_emails()
    # print(f"📧 Found {len(emails)} emails for today.")
    # for email in emails:
    #     result = classify_email(email)
    #     print(f"\n📧 Subject: {email['subject']}")
    #     print(f"✅ Is Job Application? {result['is_job_application']}")
    #     print(f"💡 Reason: {result['reason']}")


    #     if not result["is_job_application"]:
    #         print("❌ Not a job application email, skipping extraction.")
    #         continue

    #     info = extract_email_content(email)
    #     print(f"🏢 Company: {info['company']}")
    #     print(info, "-----info-----")
    #     write_to_sheet(info)
    graph = build_graph()
    graph.invoke({})
    
       


if __name__ == "__main__":
    main()