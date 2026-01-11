
from utils import init_sheet_client
import os 
import gspread
from typing import Optional
import logging

logger = logging.getLogger(__name__)



SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Sheet1")
def update_status_agent(email_data, sheet_data_cache: Optional[dict] = None):
    """
    Update the status of a job application based on the email data.

    Args:
        email_data (dict): A dictionary containing email information. Expected keys include
            'company', 'job_title', 'submission_date', and 'email_id'.
        sheet_data_cache (dict): Optional cached sheet data with lookup dictionary.

    Functionality:
        - Initializes a Google Sheets client.
        - Opens the target sheet using a predefined SHEET_ID and SHEET_NAME.
        - Uses cached lookup dictionary for O(1) row finding instead of O(N) linear search.
        - Updates the status cell directly.
    """

    current_company_name = email_data.get('company')
    current_job_title = email_data.get('job_title')
    status = email_data.get('status', 'Updated')  # Default to 'Updated' if status is not provided

    # Use cached lookup if available for O(1) performance
    if sheet_data_cache and 'row_lookup' in sheet_data_cache:
        lookup_key = (current_company_name, current_job_title)
        row_index = sheet_data_cache['row_lookup'].get(lookup_key)
        
        if row_index:
            client = init_sheet_client()
            sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
            logger.info(f"Updating status for {current_company_name} - {current_job_title}")
            try:
                sheet.update_cell(row_index, 4, status)
                return f"Status updated for {current_company_name} - {current_job_title} to {status}"
            except gspread.exceptions.APIError as e:
                logger.error(f"❌ Error updating Google Sheet: {e}")
                return f"Error updating {current_company_name} - {current_job_title}"
        return f"No matching row found for {current_company_name} - {current_job_title}"
    
    # Fallback to original linear search if no cache
    client = init_sheet_client()
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    
    company_names = sheet.col_values(2)
    positions = sheet.col_values(3)

    for i in range(len(company_names)):
        curr_val = company_names[i]
        curr_pos = positions[i]
        if curr_val == current_company_name and curr_pos == current_job_title:
            logger.info(f"Updating status for {current_company_name} - {current_job_title}")
            try:
                sheet.update_cell(i + 1, 4, status)
                return f"Status updated for {current_company_name} - {current_job_title} to {status}"
            except gspread.exceptions.APIError as e:
                logger.error(f"❌ Error updating Google Sheet: {e}")
            break

    
                
            










    
    



