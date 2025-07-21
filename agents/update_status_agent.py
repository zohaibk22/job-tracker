
from utils import init_sheet_client
import os 
import gspread



SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Sheet1")
def update_status_agent(email_data):
    """
    Update the status of a job application based on the email data.

    Args:
        email_data (dict): A dictionary containing email information. Expected keys include
            'company', 'job_title', 'submission_date', and 'email_id'.

    Functionality:
        - Initializes a Google Sheets client.
        - Opens the target sheet using a predefined SHEET_ID and SHEET_NAME.
        - Extracts the submission date from email_data or uses the current date if not provided.
        - Prepares a row with the date, company, job title, and email ID.
        - Appends the row to the sheet using 'USER_ENTERED' value input option.
    """
    print("IN UPDATE STATUS AGENT 🚀")

    client = init_sheet_client()
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    # Extract only the required properties from email_data['job_info']
    job_info = email_data.get('job_info', {})
    current_company_name = job_info.get('company')
    current_job_title = job_info.get('job_title')
    status = job_info.get('status', 'Updated')  # Default to 'Updated' if status is not provided

    # current_company_position

    company_names = sheet.col_values(2)
    positions = sheet.col_values(3)

    for i in range(len(company_names)):
        curr_val = company_names[i]
        curr_pos = positions[i]
        if  curr_val == current_company_name and curr_pos == current_job_title:
            print(f"Updating status for {current_company_name} - {current_job_title}")
            # Update the status in the sheet
            try:
                sheet.update_cell(i + 1, 4, status)
                return f"Status updated for {current_company_name} - {current_job_title} to {status}"
            except gspread.exceptions.APIError as e:
                print(f"❌ Error updating Google Sheet: {e}")
            break

    
                
            










    
    



