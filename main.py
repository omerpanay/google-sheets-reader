import streamlit as st
import json
from downloader import GoogleSheetsDownloader
from google_sheets_embedding_method import GoogleSheetsEmbeddingMethod
from vector_store_manager import GoogleSheetsVectorStore
from shared.config import setup_environment
import os
import time

# Environment setup
setup_environment()

def main():
    st.set_page_config(page_title="Google Sheets Reader", layout="wide")
    st.title("📊 Google Sheets Reader")

    # Google credentials JSON input
    st.subheader("🔑 Google Service Account Credentials")
    credentials_text = st.text_area(
        "Paste the credentials JSON here:",
        height=200,
        placeholder='{\n  "type": "service_account",\n  "project_id": "your-project",\n  "private_key_id": "...",\n  ...\n}',
        help="Paste the contents of the downloaded Google Cloud Service Account JSON file."
    )

    # Spreadsheet ID input
    st.subheader("📄 Google Sheets Information")
    spreadsheet_id = st.text_input(
        "Enter Google Sheets ID:",
        placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
        help="Paste the ID part from the Google Sheets URL."
    )

    st.subheader("🚀 One-Click Run")
    st.caption("This button will: download & display data, build embeddings, save to the vector store, then show statistics.")

    if credentials_text and spreadsheet_id and st.button("Start Process"):
        
        try:
            # Parse JSON
            try:
                credentials_data = json.loads(credentials_text)
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON format: {e}")
                return
            
            # 1. DOWNLOAD & DISPLAY DATA
            with st.spinner("📥 Downloading Google Sheets data..."):
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                    json.dump(credentials_data, tmp_file)
                    tmp_file_path = tmp_file.name
                try:
                    downloader = GoogleSheetsDownloader(tmp_file_path)
                    spreadsheet_info = downloader.get_spreadsheet_info(spreadsheet_id)
                    all_data = downloader.download_all_sheets(spreadsheet_id)
                finally:
                    os.unlink(tmp_file_path)

            st.success(f"📄 Title: {spreadsheet_info['title']}")
            sheet_names = list(all_data.keys())
            sheet_count = len(sheet_names)
            total_rows = sum(max(0, len(data) - 1) for data in all_data.values())  # exclude header row
            st.info(f"� Sheets: {sheet_names}")
            st.caption(f"Summary: {sheet_count} sheet(s), {total_rows} total data row(s) (headers excluded).")

            # 2. EMBEDDING & VECTOR STORE
            with st.spinner("🤖 Generating embeddings and saving to vector store..."):
                try:
                    embedding_method = GoogleSheetsEmbeddingMethod(
                        credentials_json=credentials_text,
                        spreadsheet_id=spreadsheet_id
                    )
                    documents = embedding_method.get_documents("google_sheets")
                    if not documents:
                        st.error("❌ No documents found, embedding skipped.")
                        return
                    nodes = embedding_method.create_nodes(documents)
                    vector_store = GoogleSheetsVectorStore(
                        collection_name=f"sheets_{spreadsheet_id[:8]}"
                    )
                    vector_store.create_index(nodes)
                    stats = vector_store.get_stats()
                except Exception as e:
                    st.error(f"❌ Embedding/Vector store error: {e}")
                    return

            st.success("✅ Embedding and storage completed")
            st.json({
                "📊 Document Count": len(documents),
                "🧩 Node Count": len(nodes),
                "🗄️ Collection": stats["collection_name"],
                "📈 Total Records": stats["document_count"]
            })

            # 3. STATS (optional detail)
            with st.expander("📈 Detailed Vector Store Statistics"):
                st.json(stats)
                st.caption("All steps completed successfully.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        # Usage guidance
        if not credentials_text:
            st.info("🔑 Please enter the Google Service Account credentials JSON.")
        if not spreadsheet_id:
            st.info("📄 Please enter the Google Sheets ID.")
        
        # Help section
        with st.expander("❓ How to Use"):
            st.markdown("""
            ### Create a Google Service Account:
            1. Go to [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
            2. Click "Create Credentials" → "Service account"
            3. After creating, go to the service account → "Keys" → "Add key" → "Create new key" → JSON
            4. Open the downloaded JSON and paste its content above.

            ### Find the Google Sheets ID:
            - Copy the ID from the sheet URL:
            - `https://docs.google.com/spreadsheets/d/`**`ID_HERE`**`/edit`

            ### Important:
            - Share the Sheet with the service account email as at least a Viewer.
            """)
        
        # Sample JSON
        with st.expander("📝 Sample Credentials JSON"):
            st.code('''
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "abcd1234...",
  "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",
  "client_email": "your-service@your-project.iam.gserviceaccount.com",
  "client_id": "123456789...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/..."
}
            ''', language='json')

if __name__ == "__main__":
    main()
