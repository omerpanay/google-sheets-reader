from typing import Sequence, List
from shared.protocol import EmbeddingMethod
from llama_index.core.schema import Document, BaseNode
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.google import GoogleSheetsReader
import os
import json


class GoogleSheetsEmbeddingMethod(EmbeddingMethod):
    """Embedding method for Google Sheets"""

    def __init__(self, spreadsheet_id: str, credentials_path: str = None):
        self.spreadsheet_id = spreadsheet_id
        self.credentials_path = credentials_path or "credentials.json"

    @staticmethod
    def customize_metadata(document: Document, data_source_id: str, **kwargs) -> Document:
        document.metadata.update({
            "data_source": data_source_id,
            "source_type": "google_sheets"
        })
        return document

    def get_documents(self, data_source_id: str = "google_sheets") -> Sequence[Document]:
        try:
            # Environment variable olarak credentials ayarla
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
            print(f"[LOG] (Sheets) Using credentials: {self.credentials_path}")
            
            # GoogleSheetsReader'ı parametresiz kullan (environment variable'dan okur)
            reader = GoogleSheetsReader()
            documents = reader.load_data(spreadsheet_id=self.spreadsheet_id)
            print(f"[LOG] (Sheets) Documents loaded: {len(documents)}")
            return [self.customize_metadata(doc, data_source_id) for doc in documents]
        except Exception as e:
            print(f"❌ Error loading from Google Sheets: {e}")
            return []

    def download_and_process(self) -> Sequence[Document]:
        return self.get_documents()

    def create_nodes(self, documents: Sequence[Document]) -> List[BaseNode]:
        pipeline = IngestionPipeline(
            transformations=[
                SentenceSplitter(chunk_size=1024, chunk_overlap=50)
            ]
        )
        return pipeline.run(documents=documents)

    def process(
        self,
        vector_store,
        task_manager,
        data_source_id: str,
        task_id: str,
        **kwargs,
    ) -> None:
        # Eğer streamlit içinde embedding yapmak istersen bu kısmı kullanabilirsin
        pass
