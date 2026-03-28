import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict
from src.utils.config import Config
import logging

class GoogleSheetsSync:
    def __init__(self):
        self.logger = logging.getLogger("integrations.gsheet")
        self.logger.setLevel(logging.INFO)
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.client = self._authenticate()

    def _authenticate(self):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(Config.GSHEET_CREDENTIALS_JSON, self.scope)
            return gspread.authorize(creds)
        except Exception as e:
            self.logger.error(f"Failed to authenticate Google Sheets: {e}")
            return None

    def sync_startups(self, startups: List[Dict]):
        """
        Syncs a list of evaluated startups to the configured Google Sheet.
        """
        if not self.client:
            self.logger.warning("No Google Sheets client, skipping sync...")
            return

        try:
            sheet = self.client.open(Config.GSHEET_NAME).sheet1
            
            # Prepare header if sheet is empty
            if not sheet.get_all_values():
                header = [
                    "Company Name", "Website", "Email", "Description", 
                    "Industry", "Stage", "Amount Raising", "Founders", 
                    "LinkedIn", "SDG Impact", "Confidence Score", 
                    "Recommendation", "Status"
                ]
                sheet.append_row(header)

            for startup in startups:
                row = [
                    startup.get("company_name", ""),
                    startup.get("website", ""),
                    startup.get("email", "n/a"),
                    startup.get("description", ""),
                    startup.get("industry", ""),
                    startup.get("stage", ""),
                    startup.get("funding_info", ""),
                    startup.get("founders", "n/a"),
                    startup.get("linkedin", "n/a"),
                    startup.get("sdg_alignment", ""),
                    startup.get("confidence_score", 0),
                    startup.get("recommendation", ""),
                    "Pending"
                ]
                sheet.append_row(row)
                self.logger.info(f"Synced {startup.get('company_name')} to Google Sheets")
                
        except Exception as e:
            self.logger.error(f"Error syncing to Google Sheets: {e}")
