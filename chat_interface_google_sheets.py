import streamlit as st
from shared.llama_utils import setup_llama_index, create_index_from_documents
from shared.config import setup_environment
from llama_index.readers.google import GoogleSheetsReader
from llama_index.core import Document
import json

def run_sheets_chat(spreadsheet_id):
    """Reads a specific Google Sheet document"""
    setup_environment()
    setup_llama_index()

    st.title("📊 Google Sheets Reader")
    st.write("Reading document from Google Sheets...")

    try:
        with open("credentials.json", 'r', encoding='utf-8') as f:
            service_account_key = json.load(f)

        reader = GoogleSheetsReader(service_account_key=service_account_key)
        documents = reader.load_data(spreadsheet_id=spreadsheet_id)

        if not documents:
            st.warning("No data found in the spreadsheet.")
            return

        index = create_index_from_documents(documents)
        st.success("Spreadsheet successfully read and index created!")

        st.write("### Sheets Read:")
        for doc in documents:
            st.write(f"- {doc.metadata.get('sheet_name', 'Unnamed Sheet')}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
