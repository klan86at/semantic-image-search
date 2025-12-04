from qdrant_client import QdrantClient
from qdrant_client.http import models
from semantic_image_search.backend.config import Config
from semantic_image_search.backend.logger import GLOBAL_LOGGER as log
from semantic_image_search.backend.exception.custom_exception import SemanticImageSearchException


class QdrantClientManager:
    """
    Manages Qdrant client connection and collection setup.
    Implements singleton pattern for client instance.
    """
    _client = None

    @classmethod
    def get_client(cls) -> QdrantClient:
        """Lazy initialize the Qsrant client"""
        if cls._client is None:

            if not Config.QDRANT_URL:
                log.warning("QDRANT_URL missing in environment")

            if not Config.QDRANT_API_KEY:
                log.warning("QDRANT_API_KEY missing in environment")

            log.info(
                "Initializing Qdrant client",
                url=Config.QDRANT_URL,
                using_api_key=bool(Config.QDRANT_API_KEY)
            )
            try:
                log.info("Creating new Qdrant client", url=Config.QDRANT_URL)
                cls._client = QdrantClient(
                    url=Config.QDRANT_URL,
                    api_key=Config.QDRANT_API_KEY
                )
                log.info("Qdrant client created successfully")

            except Exception as e:
                log.error("Failed to create Qdrant client", error=str(e))
                raise SemanticImageSearchException("Error creating Qdrant client", e)
            
        return cls._client

    @classmethod
    def ensure_collection(cls):
        """Ensure the Qdrant collection exists, create if missing"""

        try:
            client = cls.get_client()

            log.info("Fetching exizting Qdrant collections...")

            all_collections = client.get_collections().collections
            existing = {c.name for c in all_collections}

            if Config.QDRANT_COLLECTION not in existing:

                log.info(
                    "Creating new Qdrant collection",
                    collection=Config.QDRANT_COLLECTION,
                    vector_size=Config.VECTOR_SIZE,
                    distance="COSINE",
                )
                client.create_collection(
                    collection_name=Config.QDRANT_COLLECTION,
                    vectors={
                        "default": models.VectorParams(
                            size=Config.VECTOR_SIZE,
                            distance=models.Distance.COSINE,
                            on_disk=True, # important for large datasets
                        )
                    },
                    
                )

                log.info("Qdrant collection created", collection=Config.QDRANT_COLLECTION)

            else:
                log.info(
                    "Using existing Qdrant collection",
                    collection=Config.QDRANT_COLLECTION
                )

        except Exception as e:
            log.error("Failed to ensure Qdrant collection", error=str(e))
            raise SemanticImageSearchException("Error ensuring Qdrant collection", e)

      
if __name__ == "__main__":
    client = QdrantClientManager.get_client()
    QdrantClientManager.ensure_collection()