from typing import Sequence, List
from llama_index.core.schema import Document, BaseNode
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.google import GoogleSheetsReader
import json
import tempfile
import os

class GoogleSheetsEmbeddingMethod:
    """Embedding method for Google Sheets - Simplified version"""

    def __init__(self, credentials_json: str, spreadsheet_id: str):
        self.credentials_json = credentials_json
        self.spreadsheet_id = spreadsheet_id

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

    def get_documents(self, data_source_id: str = "google_sheets") -> Sequence[Document]:
        """Get documents from Google Sheets"""
        try:
            print(f"🔍 Debug: Starting document loading from sheet ID: {self.spreadsheet_id}")

            # 1) Credentials JSON'u doğrula
            credentials_data = json.loads(self.credentials_json)
            print("🔍 Debug: Credentials JSON parsed")

            # 2) Geçici dosya oluştur & env var ayarla
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                json.dump(credentials_data, tmp_file)
                tmp_file_path = tmp_file.name
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_file_path
            print(f"🔍 Debug: GOOGLE_APPLICATION_CREDENTIALS set -> {tmp_file_path}")

            documents: Sequence[Document] = []
            try:
                # 3) Parametresiz reader (yeni LlamaIndex sürümlerinde env'den okur)
                reader = GoogleSheetsReader()
                print("🔍 Debug: GoogleSheetsReader instantiated (no args)")
                documents = reader.load_data(spreadsheet_id=self.spreadsheet_id)
                print(f"🔍 Debug: Reader returned {len(documents)} document(s)")
            except TypeError as te:
                # Olur da farklı bir signature varsa bilgi ver
                print(f"⚠️ Debug: TypeError on GoogleSheetsReader usage: {te}")
            except Exception as re:
                print(f"⚠️ Debug: Reader load exception: {re}")
            finally:
                # Geçici dosyayı hemen silme; bazı client'lar lazy okuyabilir, aşağıda silinecek
                pass

            # 4) Fallback: Eğer hala döküman yoksa manuel indir & Document oluştur
            if not documents:
                print("⚠️ Debug: Fallback -> manual download via GoogleSheetsDownloader")
                try:
                    from downloader import GoogleSheetsDownloader
                    manual_downloader = GoogleSheetsDownloader(tmp_file_path)
                    info = manual_downloader.get_spreadsheet_info(self.spreadsheet_id)
                    all_data = manual_downloader.download_all_sheets(self.spreadsheet_id)
                    from llama_index.core.schema import Document as LlamaDocument
                    built_docs: List[Document] = []
                    for sheet_name, rows in all_data.items():
                        if not rows:
                            continue
                        # Birinci satır header ise atla; metni satırları birleştirerek oluştur
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
                    print(f"🔍 Debug: Fallback built {len(documents)} document(s)")
                except Exception as fe:
                    print(f"❌ Fallback failed: {fe}")

            # 5) Metadata zenginleştirme
            for document in documents:
                self.customize_metadata(
                    document,
                    data_source_id,
                    spreadsheet_id=self.spreadsheet_id
                )
            print("🔍 Debug: Metadata customization done")

            return documents

        except json.JSONDecodeError as je:
            print(f"❌ Credentials JSON decode error: {je}")
            return []
                
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
