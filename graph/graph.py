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

def fetch_node(state) -> dict:
    print('**************************** IN FETCH NODE ****************************')
    emails = fetch_today_emails()

    return {
        **state,
        "emails": emails,
        "index": 0
    }


def classify_node(state):
    print('**************************** IN CLASSIFY NODE ****************************')
    index = state["index"] or 0
    email = state["emails"][index]

    result = classify_email(email)

    state["email"] = email
    state["email_id"] = email.get("id")
    state["is_relevant"] = result["is_job_application"]
    state["reason"] = result["reason"]
    state["status"] = result["status"]
    return state

def extract_node(state):
    print('**************************** IN EXTRACT NODE ****************************')
    info = extract_email_content(state["email"])
    # state["job_info"] = info  # update in-place
    state["job_info"] = info
    return state

def write_node(state):
    print('**************************** IN EXTRACT NODE ****************************')
    print(state, '------STATE IN WRITE NODE------')
    job_details = write_to_sheet({**state["job_info"], 'email_id': state.get("email_id"), "status": state['status']})
    if "parsed_email_list" not in state or state["parsed_email_list"] is None:
        state["parsed_email_list"] = []
    state["parsed_email_list"].append(job_details)
    return state

def write_next_node(state):
    print('**************************** IN WRITE NEXT NODE ****************************')
    print(state, '------STATE IN WRITE NEXT NODE------')
    next_index = state['index'] + 1
    state['index'] = next_index
    state['end_graph'] = next_index >= len(state['emails'])
    return state
        

def update_status_node(state):
    print('**************************** IN UPDATE STATUS NODE ****************************')
    publish_data = update_status_agent(state['job_info'])
    if "parsed_email_list" not in state or state["parsed_email_list"] is None:
        state["parsed_email_list"] = []
    state['parsed_email_list'].append(publish_data)
    return state

def publish_results(state):
    print('**************************** IN PUBLISH RESULTS NODE ****************************')
    # Here you would implement the logic to publish the results
    # For example, sending an email or updating a dashboard
    publisher = EventPublisher('email_notifications_channel')
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

    graph.add_edge("fetch_emails", "classify_email")

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
    lambda state: "classify_email" if not state['end_graph'] else publish_results(state)
    )
    graph.add_edge('publish_results', END)

    return graph.compile()
