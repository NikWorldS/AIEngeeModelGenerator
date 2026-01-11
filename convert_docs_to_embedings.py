import time

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from qdrant_client.models import PointStruct, VectorParams, Distance
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import UpdateStatus
from qdrant_client import QdrantClient

from os.path import join
import uuid
import json
import os


class QDRANT_PARAMS:
    HOST = ""
    PORT = ""
    COLLECTION_NAME = "test_collection_DOT"

class CHUNK_PARAMS:
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 25
    SEPARATORS: list[str] = ["\n\n", "\n", ". "]

class DocsConverter:
    def __init__(self):
        self.__base_dir = "documentation"
        if not os.path.exists(self.__base_dir):
            raise FileExistsError(f'"{self.__base_dir}" folder not found!')

        self.__text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_PARAMS.CHUNK_SIZE,
            chunk_overlap=CHUNK_PARAMS.CHUNK_OVERLAP,
            separators=CHUNK_PARAMS.SEPARATORS
        )

        self.__embedding_model = SentenceTransformer(
            model_name_or_path="ai-forever/ru-en-RoSBERTa"
        )

        self.__qdrant_client = QdrantClient(url="http://localhost:6333")
        self.__create_qdrant_collection()

    def __create_qdrant_collection(self):
        try:
            self.__qdrant_client.get_collection(QDRANT_PARAMS.COLLECTION_NAME)
        except UnexpectedResponse:
            self.__qdrant_client.create_collection(
                collection_name=QDRANT_PARAMS.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.__embedding_model.get_sentence_embedding_dimension(),
                    distance=Distance.DOT
                ),
        )

    @staticmethod
    def get_token_count(text: str) -> int:
        return len(text.split())

    def get_split_chunks(self, document_text: str) -> list[str]:
        try:
            return self.__text_splitter.split_text(document_text)
        except:
            return []

    def __get_block_metadata(self, file_name: str) -> dict[str, str]:
        metadata_text: str = open(join(self.__base_dir, file_name) + ".json", "r", encoding="utf-8").read()
        metadata: dict = json.loads(metadata_text)
        return metadata


    def get_files_list(self) -> list[str]:
        files_list = os.listdir(self.__base_dir)
        if files_list:
            files_name = set([file.rsplit('.', 1)[0] for file in files_list])

            return list(files_name)
        else:
            raise FileNotFoundError(f"No files in '{self.__base_dir}' directory!")

    def get_embedding(self, chunk_text):
        embedding = self.__embedding_model.encode(
            chunk_text
            ).tolist()
        return embedding

    def construct_payload(self, payload_text, section_name, metadata: dict[str, str]) -> dict[str, str]:
        payload = {
            "block_name": metadata.get("block_name"),
            "block_path": metadata.get("block_path"),
            "section_name": section_name,
            "text": payload_text,
        }

        return payload

    def construct_points(self, chunks: list[dict[str, str]], metadata: dict[str, str]) -> list[PointStruct]:
        points: list[PointStruct] = []

        for chunk in chunks:
            chunk_text, section_name, payload_text = chunk.values()
            point = PointStruct(
                id=str(uuid.uuid4().hex),
                vector=self.get_embedding(chunk_text),
                payload=self.construct_payload(payload_text, section_name, metadata),
            )
            points.append(point)
        return points

    def main_pipeline(self):
        queries_status: list[str] = []

        files_list = self.get_files_list()
        for file in files_list:
            file_size = os.path.getsize(join(self.__base_dir, file) + ".md") / 1024

            with open(join(self.__base_dir, file) + ".md", 'r', encoding="utf-8") as f:
                file_text = f.read()

            if file_size < 20:
                section_name = "root"
                section_text = file_text
                sections = [(section_name, section_text)]
            else:
                sections = self.split_by_sections(file_text)

            all_chunks = []

            for section_name, section_text in sections:
                if section_text:
                    chunks = self.__text_splitter.split_text(section_text)
                    for chunk in chunks:
                        all_chunks.append({
                            "chunk_text": chunk,
                            "section_name": section_name,
                            "text": section_text,
                        })

            metadata = self.__get_block_metadata(file)
            points = self.construct_points(all_chunks, metadata)

            operation_info = self.__qdrant_client.upsert(
                collection_name=QDRANT_PARAMS.COLLECTION_NAME,
                wait=True,
                points=points,
            )

            queries_status.append(operation_info.status)

        print(f"ВСЕГО ОПЕРАЦИЙ: {len(queries_status)}")
        print(f"УСПЕШНЫХ ОПЕРАЦИЙ: {queries_status.count(UpdateStatus.COMPLETED)}")

    def split_by_sections(self, md_text: str) -> list[tuple[str, str]]:
        sections = []
        current_name = "root"
        current_lines = []

        for line in md_text.splitlines():
            if line.startswith("## "):
                if current_lines:
                    sections.append((current_name, "\n".join(current_lines).strip()))
                current_name = line[3:].strip()
                current_lines = []
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_name, "\n".join(current_lines).strip()))

        return sections



if __name__ == '__main__':
    doc_converter = DocsConverter()

    start_time = time.perf_counter()

    doc_converter.main_pipeline()

    end_time = time.perf_counter()
    print(f"\nЗАТРАЧЕНО ВРЕМЕНИ НА ВЕКТОРИЗАЦИЮ: {end_time - start_time:.2f}s")