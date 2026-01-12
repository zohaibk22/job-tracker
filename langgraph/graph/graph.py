import json
import operator
from langgraph.graph import StateGraph, END
from agents import fetch_today_emails
from agents import classify_email
from agents import extract_email_content
from agents import write_to_sheet
from agents import update_status_agent
from typing import TypedDict, Optional
from typing_extensions import Annotated

from publisher import EventPublisher

from utils import init_sheet_client
import os
import logging

logger = logging.getLogger(__name__)
    

# Step 1: Define each LangGraph-compatible node

class GraphState(TypedDict, total=False):
    emails: list # Annotated to handle multiple values
    email: dict
    email_id: Optional[str]  # Optional, if you want to track email IDs
    is_relevant: bool
    reason: str
    job_info: dict
    index: int
    end_graph: bool
    status: str
    parsed_email: str
    parsed_email_list: list
    sheet_data_cache: dict  # Cache for sheet data to avoid repeated API calls

def fetch_node(state) -> dict:
    logger.info('**************************** IN FETCH NODE ****************************')
    emails = fetch_today_emails()
    logger.info(f"Fetched {len(emails)} emails.")

    # Build sheet data cache once at the start
  
    SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Sheet1")
    
    try:
        client = init_sheet_client()
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        
        # Load all data once
        email_ids = set(sheet.col_values(5))  # Column 5 has email IDs
        company_names = sheet.col_values(2)   # Column 2 has companies
        positions = sheet.col_values(3)       # Column 3 has job titles
        
        # Build O(1) lookup dictionary: "company|title" -> row_index
        row_lookup = {}
        for i in range(len(company_names)):
            if i < len(positions):  # Safety check
                key = f"{company_names[i]}|{positions[i]}"  # String key instead of tuple
                row_lookup[key] = i + 1  # 1-indexed for sheet API
        
        sheet_data_cache = {
            'email_ids': email_ids,
            'row_lookup': row_lookup
        }
        logger.info(f"Built sheet cache with {len(email_ids)} email IDs and {len(row_lookup)} entries")
    except Exception as e:
        logger.error(f"Warning: Could not build sheet cache: {e}")
        sheet_data_cache = {'email_ids': set(), 'row_lookup': {}}

    return {
        **state,
        "emails": emails,
        "index": 0,
        "sheet_data_cache": sheet_data_cache
    }


def classify_node(state):
    logger.info('**************************** IN CLASSIFY NODE ****************************')
    index = state.get("index", 0)
    email = state["emails"][index]

    result = classify_email(email)

    return {
        **state,
        "email": email,
        "email_id": email.get("id"),
        "is_relevant": result["is_job_application"],
        "reason": result["reason"],
        "status": result["status"]
    }

def extract_node(state):
    logger.info('**************************** IN EXTRACT NODE ****************************')
    info = extract_email_content(state["email"])
    return {
        **state,
        "job_info": info
    }

def write_node(state):
    logger.info('**************************** IN WRITE NODE ****************************')
    sheet_cache = state.get('sheet_data_cache', None)
    job_details = write_to_sheet(
        {**state["job_info"], 'email_id': state.get("email_id"), "status": state['status']},
        sheet_data_cache=sheet_cache
    )
    parsed_list = state.get("parsed_email_list", [])
    if parsed_list is None:
        parsed_list = []
    
    return {
        **state,
        "parsed_email_list": parsed_list + [job_details]
    }

def write_next_node(state):
    logger.info('**************************** IN WRITE NEXT NODE ****************************')
    next_index = state['index'] + 1
    end_graph = next_index >= len(state['emails'])
    
    return {
        **state,
        'index': next_index,
        'end_graph': end_graph
    }
        

def update_status_node(state):
    logger.info('**************************** IN UPDATE STATUS NODE ****************************')
    sheet_cache = state.get('sheet_data_cache', None)
    publish_data = update_status_agent(state['job_info'], sheet_data_cache=sheet_cache)
    
    parsed_list = state.get("parsed_email_list", [])
    if parsed_list is None:
        parsed_list = []
    
    return {
        **state,
        'parsed_email_list': parsed_list + [publish_data]
    }

def publish_results(state):
    logger.info('**************************** IN PUBLISH RESULTS NODE ****************************')
    # Here you would implement the logic to publish the results
    # For example, sending an email or updating a dashboard
    publisher = EventPublisher('email_notifications_channel')
    if 'parsed_email_list' not in state or state['parsed_email_list'] is None:
        state['parsed_email_list'] = []
    logger.info(f"Total emails: {len(state['emails'])}")
    if len(state['parsed_email_list']) == 0:
        publisher.publish(json.dumps([{"message": "No emails found today."}]))
    publisher.publish(json.dumps(state['parsed_email_list']))
    return state

# Step 2: Build the graph
def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("fetch_emails", fetch_node)
    graph.add_node("classify_email", classify_node)
    graph.add_node("extract_info", extract_node)
    graph.add_node("write_sheet", write_node)
    graph.add_node("update_status", update_status_node)
    graph.add_node("write_next", write_next_node)
    graph.add_node('publish_results', publish_results)


    # Entry point
    graph.set_entry_point("fetch_emails")
    graph.add_conditional_edges("fetch_emails", lambda state: "classify_email" if len(state["emails"]) > 0 else 'publish_results')


    # The graph processes one email at a time by using the 'index' to track the current email.
    # After processing (classify -> extract -> write), it increments 'index' and loops back if more emails remain.

    graph.add_conditional_edges(
        "classify_email",
        lambda state: "extract_info" if state["is_relevant"] else 'write_next'
    )

    graph.add_conditional_edges(
        "extract_info",
        lambda state: "update_status" if state['status'] != 'Applied' else "write_sheet"
    )

    graph.add_edge("update_status", "write_sheet")
    graph.add_edge("write_sheet", "write_next")
    graph.add_conditional_edges(
    "write_next",
    lambda state: "classify_email" if not state['end_graph'] else 'publish_results'
    )
    graph.add_edge('publish_results', END)

    return graph.compile()
