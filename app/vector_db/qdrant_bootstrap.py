from qdrant_client import QdrantClient

from app.vector_db.qdrant_restore import QdrantRestore


class QdrantBootstrap:
    def __init__(self, client: QdrantClient, restore_service: QdrantRestore, collection_name: str) -> None:
        self.client = client
        self.restore_service = restore_service
        self.collection_name = collection_name

    def ensure_ready(self) -> None:
        if self.__collection_exists() and not self.__collection_is_empty():
            return

        if self.restore_service.snapshot_exists_in_folder():
            restore_res = self.restore_service.restore_from_snapshot()
            if restore_res:
                return
            else:
                raise RuntimeError(f"Failed to restore snapshot")

        raise RuntimeError(f"Collection {self.collection_name} is missing or empty, snapshot was not found")


    def __collection_exists(self) -> bool:
        return self.client.collection_exists(self.collection_name)

    def __collection_is_empty(self) -> bool:
        return self.client.count(self.collection_name) == 0