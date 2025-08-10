from abc import ABC, abstractmethod

class EmbeddingMethod(ABC):
    """Abstract base class for embedding methods."""

    @abstractmethod
    def get_documents(self):
        pass

    @abstractmethod
    def create_nodes(self, documents):
        pass