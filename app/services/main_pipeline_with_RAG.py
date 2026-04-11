import json

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.exceptions import UnexpectedResponse
from sentence_transformers import SentenceTransformer
from ollama import Client
import os


class OLLAMA_PARAMS:
    """Parameters for OLLAMA"""
    OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME")


class QDRANT_PARAMS:
    """parameters for connection to qdrant DB"""
    HOST = os.getenv("QDRANT_HOST", "localhost")
    PORT = os.getenv("QDRANT_PORT", "6333")
    COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

    @property
    def get_qdrant_url(self) -> str:
        """Return the qdrant url for connecting"""
        return f"http://{self.HOST}:{self.PORT}"


class MainPipeline:
    """Main pipeline for model response using context from qdrant vector database"""

    def __init__(self):
        self.__embedding_model = SentenceTransformer(
            model_name_or_path="ai-forever/ru-en-RoSBERTa",
            device="cuda",
        )

        self.__ollama_client = Client()

        self.__qdrant_client = QdrantClient(url=QDRANT_PARAMS.get_qdrant_url)
        self.__create_qdrant_collection(QDRANT_PARAMS.COLLECTION_NAME)

    def __create_qdrant_collection(self, collection_name) -> None:
        """Create the qdrant collection if its not exists with the given name"""
        try:
            self.__qdrant_client.get_collection(collection_name)
        except UnexpectedResponse:
            self.__qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.__embedding_model.get_sentence_embedding_dimension(),
                    distance=Distance.DOT
                ),
            )

    def __get_embedding(self, chunk_text) -> list[list[float]]:
        """Return the embedding of the chunk text"""
        embedding = self.__embedding_model.encode(
            chunk_text
        ).tolist()
        return embedding

    def query(self):
        pass

    def get_contexts(self, prompt_text: str) -> list[str]:
        """Return list with 5 closest to prompt records (block describes)"""
        context_list: list[str] = []

        results = self.__qdrant_client.query_points(
            collection_name=QDRANT_PARAMS.COLLECTION_NAME,
            query=self.__get_embedding(prompt_text),
            limit=5,
            with_payload=True
        )

        for _, scope in results:
            for point in scope:
                context_list.append(point.payload)

        return context_list

    def get_system_prompt(self, context_text: str) -> str:
        """Return system prompt with adding context text"""
        SYSTEM_PROMPT = f"""
        Ты ассистент, который генерирует скрипты для Engee.
        Требования:
        - Отвечай ТОЛЬКО кодом, без пояснений.
        - Используй функции engee.create, engee.add_block, engee.set_param!, engee.add_line, engee.save.
        - Код ОБЯЗАТЕЛЬНО должен компилироваться и работать без ошибок.
        - Анализируй контекст из базы знаний (в ней представлена документация блоков: путь в библиотеке, описание, параметры, порты)
        - На основе этой информации напиши требуемый скрипт на языке Julia
        
        Контекст документации блоков: <CONTEXT_START>{" ".join(str(context_text))}<CONTEXT_END>
                
        Всегда используй только:
        - engee.create
        - engee.add_block
        - engee.set_param!
        - engee.add_line
        - engee.arrange_system
        - engee.save

        Всегда отвечай только кодом Julia, без пояснений.


        # Инструкция:
        - Не выводи пояснений, отвечай только кодом
        
        Пример 1.
        Задание: <<Построй простую модель: два блока Constant, их сумма через Add и один выходной порт с результатом.>>
        Ответ:
        <<engee.create("sum_of_constants")
        
        engee.add_block("/Basic/Sources/Constant", "sum_of_constants/Const1")
        engee.set_param!("sum_of_constants/Const1", "Value" => 2.0)
        
        engee.add_block("/Basic/Sources/Constant", "sum_of_constants/Const2")
        engee.set_param!("sum_of_constants/Const2", "Value" => 5.0)
        
        engee.add_block("/Basic/Math Operations/Add", "sum_of_constants/Add")
        engee.set_param!("sum_of_constants/Add", "Inputs" => "++")
        
        engee.add_block("/Basic/Ports & Subsystems/Out1", "sum_of_constants/Out")
        
        engee.add_line("Const1/1", "Add/1")
        engee.add_line("Const2/1", "Add/2")
        engee.add_line("Add/1", "Out/1")
        
        engee.save("sum_of_constants", "sum_of_constants.engee", force=true)
        >>
        """
        return SYSTEM_PROMPT


    def get_messages(self, user_prompt: str, context: str) -> list[dict[str, str]]:
        """Return list of messages with system, assistant and user messages"""
        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.get_system_prompt(context)},

            {"role": "user", "content": "\r\nПострой простую модель: два блока Constant, их сумма через Add и один выходной порт с результатом.\r\n"},
            {"role": "assistant", "content": "\r\nengee.create(\"sum_of_constants\")\r\n\r\n# Две константы\r\nengee.add_block(\"/Basic/Sources/Constant\", \"sum_of_constants/Const1\")\r\nengee.set_param!(\"sum_of_constants/Const1\", \"Value\" =\u003e 2.0)\r\n\r\nengee.add_block(\"/Basic/Sources/Constant\", \"sum_of_constants/Const2\")\r\nengee.set_param!(\"sum_of_constants/Const2\", \"Value\" =\u003e 5.0)\r\n\r\n# Сумматор\r\nengee.add_block(\"/Basic/Math Operations/Add\", \"sum_of_constants/Add\")\r\nengee.set_param!(\"sum_of_constants/Add\", \"Inputs\" =\u003e \"++\")\r\n\r\n# Выход\r\nengee.add_block(\"/Basic/Ports \u0026 Subsystems/Out1\", \"sum_of_constants/Out\")\r\n\r\n# Соединения\r\nengee.add_line(\"Const1/1\", \"Add/1\")\r\nengee.add_line(\"Const2/1\", \"Add/2\")\r\nengee.add_line(\"Add/1\", \"Out/1\")\r\n\r\nengee.save(\"sum_of_constants\", \"sum_of_constants.engee\", force=true)\r\n"},

            {"role": "user", "content":"\r\nПострой модель уровня жидкости в резервуаре: на входе постоянный расход притока, уровень — это интеграл расхода с заданным начальным значением. На выходе — текущий уровень.\r\n"},
            {"role": "assistant", "content": "\r\nengee.create(\"tank_level\")\r\n\r\n# Постоянный приток\r\nengee.add_block(\"/Basic/Sources/Constant\", \"tank_level/Inflow\")\r\nengee.set_param!(\"tank_level/Inflow\", \"Value\" =\u003e 0.2)\r\n\r\n# Интегратор уровня: dLevel/dt = Inflow\r\nengee.add_block(\"/Basic/Continuous/Integrator\", \"tank_level/LevelInt\")\r\nengee.set_param!(\"tank_level/LevelInt\", \"InitialCondition\" =\u003e 1.0)\r\n\r\n# Выход уровня\r\nengee.add_block(\"/Basic/Ports \u0026 Subsystems/Out1\", \"tank_level/LevelOut\")\r\n\r\n# Соединения\r\nengee.add_line(\"Inflow/1\", \"LevelInt/1\")\r\nengee.add_line(\"LevelInt/1\", \"LevelOut/1\")\r\n\r\nengee.save(\"tank_level\", \"tank_level.engee\", force=true)\r\n"},

            {"role": "user", "content": "\r\nПострой модель динамики температуры, где есть нагрев и охлаждение: два входа (положительный и отрицательный вклад), сумматор с конфигурацией +-, интегратор температуры и выход.\r\n"},
            {"role": "assistant", "content": "\r\nengee.create(\"heat_balance\")\r\n\r\n# Нагрев (положительный вклад)\r\nengee.add_block(\"/Basic/Sources/Constant\", \"heat_balance/Heating\")\r\nengee.set_param!(\"heat_balance/Heating\", \"Value\" =\u003e 4.0)\r\n\r\n# Охлаждение (отрицательный вклад)\r\nengee.add_block(\"/Basic/Sources/Constant\", \"heat_balance/Cooling\")\r\nengee.set_param!(\"heat_balance/Cooling\", \"Value\" =\u003e 3.0)\r\n\r\n# Баланс тепла: q_net = Heating - Cooling\r\nengee.add_block(\"/Basic/Math Operations/Add\", \"heat_balance/Sum\")\r\nengee.set_param!(\"heat_balance/Sum\", \"Inputs\" =\u003e \"+-\")\r\n\r\n# Интегратор температуры\r\nengee.add_block(\"/Basic/Continuous/Integrator\", \"heat_balance/TempInt\")\r\nengee.set_param!(\"heat_balance/TempInt\", \"InitialCondition\" =\u003e 80.0)\r\n\r\n# Выходная температура\r\nengee.add_block(\"/Basic/Ports \u0026 Subsystems/Out1\", \"heat_balance/TempOut\")\r\n\r\n# Соединения\r\nengee.add_line(\"Heating/1\", \"Sum/1\")\r\nengee.add_line(\"Cooling/1\", \"Sum/2\")\r\nengee.add_line(\"Sum/1\", \"TempInt/1\")\r\nengee.add_line(\"TempInt/1\", \"TempOut/1\")\r\n\r\nengee.save(\"heat_balance\", \"heat_balance.engee\", force=true)\r\n"},


            {"role": "user", "content": "твоя текущая задача - составить скрипт по следующему от пользователя указанию: " + user_prompt},
        ]
        return messages


    def main(self):
        """Gets user prompt, augmenting with context from db and return model response"""
        user_prompt = str(input("Введите промпт:\n"))

        context = self.get_contexts(user_prompt)

        messages = self.get_messages(user_prompt, context)

        response = self.__ollama_client.chat(
            model=OLLAMA_PARAMS.OLLAMA_MODEL_NAME,
            messages=messages,
        )

        print(response.message.content)

if __name__ == "__main__":
    main_pipeline = MainPipeline()
    main_pipeline.main()

