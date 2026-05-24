from qdrant_client import QdrantClient
from pathlib import Path
import os


QDRANT_SNAPSHOT_PATH = "qdrant_snapshots"

class QdrantRestore:
    def __init__(self, client: QdrantClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name
        self.snapshots_dir = Path(QDRANT_SNAPSHOT_PATH).resolve()

    def snapshot_exists_in_folder(self) -> bool:
        return self.snapshots_dir.exists() and any([p for p in self.snapshots_dir.iterdir() if p.is_file() and p.suffix == ".snapshot"])

    def restore_from_snapshot(self):
        snapshots = [p for p in self.snapshots_dir.iterdir() if p.is_file() and p.suffix == ".snapshot"]
        target_snapshot = max(snapshots, key=lambda p: p.stat().st_ctime)
        return self.client.recover_snapshot(
            self.collection_name,
            str(target_snapshot),
        )
