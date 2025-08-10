import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import List, Dict, Any

class GoogleSheetsDownloader:
    def __init__(self, credentials_file):
        self.credentials_file = credentials_file
        self.service = self._authenticate()

    def _authenticate(self):
        try:
            with open(self.credentials_file, 'r') as f:
                credentials_info = json.load(f)
            creds = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
            
            return build('sheets', 'v4', credentials=creds)
        except Exception as e:
            raise Exception(f"Google Sheets kimlik doğrulama hatası: {e}")
        
        
    def get_spreadsheet_info(self, spreadsheet_id: str) -> Dict[str, Any]:
        try:
            print(f"Attempting to access spreadsheet: {spreadsheet_id}")
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            return {
                'title': spreadsheet.get('properties', {}).get('title', 'Bilinmeyen'),
                'sheets': [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
            }
        except Exception as e:
            print(f"Error details: {str(e)}")
            print(f"Error type: {type(e)}")
            raise Exception(f"Spreadsheet bilgileri alınamadı: {e}")

    def download_sheet_data(self, spreadsheet_id: str, sheet_name: str) -> List[List[str]]:
        try:
            print(f"Downloading sheet: {sheet_name}")
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=sheet_name
            ).execute()
            return result.get('values', [])
        except Exception as e:
            print(f"Sheet download error: {str(e)}")
            raise Exception(f"{sheet_name} sheet verisi indirilemedi: {e}")

    def download_all_sheets(self, spreadsheet_id: str) -> Dict[str, List[List[str]]]:
        spreadsheet_info = self.get_spreadsheet_info(spreadsheet_id)
        all_data = {}
        for sheet_name in spreadsheet_info['sheets']:
            try:
                data = self.download_sheet_data(spreadsheet_id, sheet_name)
                all_data[sheet_name] = data
            except Exception as e:
                all_data[sheet_name] = []
                print(f"❌ {sheet_name} indirilemedi: {e}")
        return all_data
