from typing import Sequence, List, Dict, Any, Optional
from llama_index.core.schema import Document, BaseNode
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.google import GoogleSheetsReader
import json
import os
import tempfile
from contextlib import contextmanager


class InvalidDataSourceConfigException(Exception):
    pass

@contextmanager
def credentials_context(config: Dict[str, Any]):
    """Context manager to prepare temporary credentials environment.
    Steps:
      1. Save current working directory
      2. Create a temporary directory
      3. Chdir into it
      4. Write credentials JSON (service_account_dict) to token.json
      5. Set GOOGLE_APPLICATION_CREDENTIALS
      6. Yield (path to token)
      7. Revert cwd and cleanup env var automatically
    """
    original_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        token_path = os.path.join(tmpdir, "token.json")
        service_account_dict = config.get("service_account_dict", {})
        with open(token_path, "w", encoding="utf-8") as f:
            json.dump(service_account_dict, f)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = token_path
        try:
            yield token_path
        finally:
            # Clean environment
            if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") == token_path:
                del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            os.chdir(original_cwd)


class GoogleSheetsEmbeddingMethod:
    """Embedding method for Google Sheets using a config dict.

    Expected config keys:
      - service_account_dict: Dict with Google service account fields
      - spreadsheet_id: ID of the target Google Sheet
      - inclusion_rules: Optional[List[str]]
      - exclusion_rules: Optional[List[str]]
    """

    def __init__(self, data_source_id: str, config: Dict[str, Any]):
        self.validate_config(config)
        self.data_source_id = data_source_id
        self.config: Dict[str, Any] = config
        self.key = "spreadsheet_id"
        self.spreadsheet_id: str = config["spreadsheet_id"]
        self.inclusion_rules: List[str] = config.get("inclusion_rules", [])
        self.exclusion_rules: List[str] = config.get("exclusion_rules", [])

    def validate_config(self, config: Dict[str, Any]):
        required_keys = ["service_account_dict", "spreadsheet_id"]
        for k in required_keys:
            if k not in config:
                raise InvalidDataSourceConfigException(
                    f"GoogleSheetsEmbeddingMethod requires '{k}' in config."
                )
        # Validate service account fields
        required_service_account_keys = [
            "type",
            "project_id",
            "private_key_id",
            "private_key",
            "client_email",
            "client_id",
            "auth_uri",
            "token_uri",
            "auth_provider_x509_cert_url",
            "client_x509_cert_url",
            "universe_domain",
        ]
        sad = config.get("service_account_dict", {})
        for k in required_service_account_keys:
            if k not in sad:
                raise InvalidDataSourceConfigException(
                    f"GoogleSheetsEmbeddingMethod requires '{k}' in 'service_account_dict'."
                )

    def customize_metadata(self, document: Document, data_source_id: str, **kwargs) -> Document:
        document.metadata.update({
            "data_source": data_source_id,
            "source_type": "google_sheets",
            "spreadsheet_id": kwargs.get("spreadsheet_id", ""),
            "sheet_name": document.metadata.get("sheet_name", "")
        })
        return document

    def apply_rules(
        self,
        documents: Sequence[Document],
        inclusion_rules: List[str] = None,
        exclusion_rules: List[str] = None,
    ) -> Sequence[Document]:
        """Apply filtering rules to documents"""
        if not inclusion_rules and not exclusion_rules:
            return documents
            
        filtered_docs = []
        for doc in documents:
            sheet_name = doc.metadata.get("sheet_name", "").lower()
            
            # Exclusion rules kontrolü
            excluded = False
            if exclusion_rules:
                for rule in exclusion_rules:
                    if rule.lower() in sheet_name:
                        excluded = True
                        break
            
            if excluded:
                continue
                
            # Inclusion rules kontrolü (boşsa hepsini al)
            if not inclusion_rules:
                filtered_docs.append(doc)
            else:
                for rule in inclusion_rules:
                    if rule.lower() in sheet_name:
                        filtered_docs.append(doc)
                        break
        
        return filtered_docs

    def get_documents(self) -> Sequence[Document]:
        """Get documents from Google Sheets (assumes credentials_context active)."""
        try:
            print(f"🔍 Debug: Loading sheet: {self.spreadsheet_id}")
            documents: Sequence[Document] = []
            try:
                reader = GoogleSheetsReader()
                documents = reader.load_data(spreadsheet_id=self.spreadsheet_id)
                print(f"🔍 Debug: Reader returned {len(documents)} doc(s)")
            except Exception as re:
                print(f"⚠️ Debug: Primary reader exception: {re}")

            # Fallback
            if not documents:
                print("⚠️ Debug: Fallback manual download")
                try:
                    from downloader import GoogleSheetsDownloader
                    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                    manual_downloader = GoogleSheetsDownloader(cred_path)
                    all_data = manual_downloader.download_all_sheets(self.spreadsheet_id)
                    from llama_index.core.schema import Document as LlamaDocument
                    built_docs: List[Document] = []
                    for sheet_name, rows in all_data.items():
                        if not rows:
                            continue
                        text_rows = rows[1:] if len(rows) > 1 else rows
                        joined = "\n".join([", ".join(r) for r in text_rows])
                        built_docs.append(LlamaDocument(
                            text=joined,
                            metadata={
                                "sheet_name": sheet_name,
                                "row_count": len(text_rows),
                                "column_count": len(rows[0]) if rows and rows[0] else 0,
                                "fallback": True,
                            }
                        ))
                    documents = built_docs
                    print(f"🔍 Debug: Fallback built {len(documents)} doc(s)")
                except Exception as fe:
                    print(f"❌ Fallback failed: {fe}")

            # Apply metadata
            for document in documents:
                self.customize_metadata(
                    document,
                    self.data_source_id,
                    spreadsheet_id=self.spreadsheet_id
                )
            return documents
        except Exception as e:
            print(f"❌ Error loading from Google Sheets: {e}")
            return []

    def get_nodes(self, documents: Sequence[Document]) -> List[BaseNode]:
        """Convert documents to nodes"""
        pipeline = IngestionPipeline(
            transformations=[
                SentenceSplitter(chunk_size=1024, chunk_overlap=50)
            ]
        )
        return pipeline.run(documents=documents)

    def create_nodes(self, documents: Sequence[Document]) -> List[BaseNode]:
        """Create nodes from documents - alias for get_nodes"""
        return self.get_nodes(documents)
