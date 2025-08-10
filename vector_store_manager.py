import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.schema import BaseNode
from typing import List
import os

class GoogleSheetsVectorStore:
    """Vector store manager for Google Sheets documents"""
    
    def __init__(self, collection_name: str = "google_sheets_docs"):
        self.collection_name = collection_name
        self.chroma_client = None
        self.vector_store = None
        self.index = None
        self._setup_vector_store()
    
    def _setup_vector_store(self):
        """Initialize ChromaDB and vector store"""
        try:
            # ChromaDB client oluştur
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            
            # Collection oluştur veya mevcut olanı al
            collection = self.chroma_client.get_or_create_collection(self.collection_name)
            
            # ChromaVectorStore oluştur
            self.vector_store = ChromaVectorStore(chroma_collection=collection)
            
            print(f"✅ Vector store initialized: {self.collection_name}")
            
        except Exception as e:
            print(f"❌ Vector store setup error: {e}")
            raise
    
    def create_index(self, nodes: List[BaseNode]) -> VectorStoreIndex:
        """Create or update vector index with new nodes"""
        try:
            # Storage context oluştur
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # OpenAI embedding kullan
            # Ücretsiz HuggingFace embedding modeli kullan
            embed_model = HuggingFaceEmbedding(
                model_name="BAAI/bge-small-en-v1.5"
            )
            
            # Index oluştur
            self.index = VectorStoreIndex(
                nodes=nodes,
                storage_context=storage_context,
                embed_model=embed_model
            )
            
            print(f"✅ Created index with {len(nodes)} nodes")
            return self.index
            
        except Exception as e:
            print(f"❌ Index creation error: {e}")
            raise
    
    def get_stats(self) -> dict:
        """Get collection statistics"""
        try:
            if self.chroma_client:
                collection = self.chroma_client.get_collection(self.collection_name)
                count = collection.count()
                return {
                    "collection_name": self.collection_name,
                    "document_count": count,
                    "status": "active"
                }
        except Exception:
            return {
                "collection_name": self.collection_name,
                "document_count": 0,
                "status": "empty"
            }
    
    def clear_collection(self):
        """Clear all documents from collection"""
        try:
            if self.chroma_client:
                self.chroma_client.delete_collection(self.collection_name)
                collection = self.chroma_client.get_or_create_collection(self.collection_name)
                self.vector_store = ChromaVectorStore(chroma_collection=collection)
                print("✅ Collection cleared")
        except Exception as e:
            print(f"❌ Clear collection error: {e}")
