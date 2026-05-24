from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from typing import Optional

import numpy as np
import torch


class QdrantRetriever:
    def __init__(self, client: QdrantClient, collection_name: str) -> None:
        self.__client = client
        self.__collection_name = collection_name

        self.__embedding_model = SentenceTransformer(
            model_name_or_path='ai-forever/ru-en-RosBERTa',
            device='cuda' if torch.cuda.is_available() else 'cpu',
        )

    def __get_embedding(self, text: str) -> Optional[list[np.ndarray]]:
        """Return the embedding of the chunk text"""
        embedding = self.__embedding_model.encode(text).tolist()
        return embedding

    def query_points(
        self,
        query: str,
        limit: int = 5,
    ) -> list[str]:
        """
        Вовзращает лист k-лучших записей (по скору) из ВБД, похожих на запрос
        :param query: текст запроса
        :param limit: лимит записей
        :return: лист записей
        """
        embedding = self.__get_embedding(query)

        points = self.__client.query_points(
            collection_name=self.__collection_name,
            query=embedding,
            limit=limit,
            with_payload=True
        ).points

        context_list = [str(point.payload) for point in points]

        if len(context_list) == 0:
            context_list = ["Не найдено подходящих блоков"]

        return context_list
