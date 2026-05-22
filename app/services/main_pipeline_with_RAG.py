from ollama import Client

from app.core.config import Settings
from app.vector_db.retriever import QdrantRetriever


class MainPipeline:
    """Main pipeline for model response using context from qdrant vector database"""

    def __init__(self, settings: Settings, retriever: QdrantRetriever) -> None:
        self.__settings = settings
        self.__retriever = retriever

        self.__ollama_client = Client()

        # self.__create_qdrant_collection(self.__settings.qdrant_collection_name)

    # def __create_qdrant_collection(self, collection_name) -> None:
    #     """Create the qdrant collection if its not exists with the given name"""
    #     try:
    #         self.__qdrant_client.get_collection(collection_name)
    #     except UnexpectedResponse:
    #         self.__qdrant_client.create_collection(
    #             collection_name=collection_name,
    #             vectors_config=VectorParams(
    #                 size=self.__embedding_model.get_sentence_embedding_dimension(),
    #                 distance=Distance.DOT
    #             ),
    #         )

    # def get_contexts(self, prompt_text: str) -> list[str]:
    #     """Return list with 5 closest to prompt records (block describes)"""
    #     context_list: list[str] = []
    #
    #     results = self.retriever.query_points(
    #         query=self.__get_embedding(prompt_text),
    #         limit=5,
    #     )
    #
    #     points = results.points
    #     for point in points:
    #         context_list.append(str(point.payload))
    #
    #     if len(context_list) == 0:
    #         return ["Не найдено подходящих блоков"]
    #
    #     return context_list

    @staticmethod
    def get_system_prompt(context_text: list[str]) -> str:
        """Return system prompt with adding context text"""
        joined_context: str = f"\n\n\n----\n\n\n".join(context_text)

        SYSTEM_PROMPT = f"""
        Ты ассистент, который генерирует скрипты для Engee.
        Требования:
        - Отвечай ТОЛЬКО кодом, без пояснений.
        - Используй функции engee.create, engee.add_block, engee.set_param!, engee.add_line, engee.save.
        - Код ОБЯЗАТЕЛЬНО должен компилироваться и работать без ошибок.
        - Анализируй контекст из базы знаний (в ней представлена документация блоков: путь в библиотеке, описание, параметры, порты)
        - На основе этой информации напиши требуемый скрипт на языке Julia
        
        Контекст документации блоков: <CONTEXT_START>{joined_context}<CONTEXT_END>
                
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
        """
        return SYSTEM_PROMPT


    def get_messages(self, user_prompt: str, context: list[str]) -> list[dict[str, str]]:
        """Return list of messages with system, assistant and user messages"""
        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.get_system_prompt(context)},

            {"role": "user", "content": "\r\nПострой простую модель: два блока Constant, их сумма через Add и один выходной порт с результатом.\r\n"},
            {"role": "assistant", "content": "\r\nengee.create(\"sum_of_constants\")\r\n\r\n# Две константы\r\nengee.add_block(\"/Basic/Sources/Constant\", \"sum_of_constants/Const1\")\r\nengee.set_param!(\"sum_of_constants/Const1\", \"Value\" =\u003e 2.0)\r\n\r\nengee.add_block(\"/Basic/Sources/Constant\", \"sum_of_constants/Const2\")\r\nengee.set_param!(\"sum_of_constants/Const2\", \"Value\" =\u003e 5.0)\r\n\r\n# Сумматор\r\nengee.add_block(\"/Basic/Math Operations/Add\", \"sum_of_constants/Add\")\r\nengee.set_param!(\"sum_of_constants/Add\", \"Inputs\" =\u003e \"++\")\r\n\r\n# Выход\r\nengee.add_block(\"/Basic/Ports \u0026 Subsystems/Out1\", \"sum_of_constants/Out\")\r\n\r\n# Соединения\r\nengee.add_line(\"Const1/1\", \"Add/1\")\r\nengee.add_line(\"Const2/1\", \"Add/2\")\r\nengee.add_line(\"Add/1\", \"Out/1\")\r\n\r\nengee.save(\"sum_of_constants\", \"sum_of_constants.engee\", force=true)\r\n"},

            {"role": "user", "content":"\r\nПострой модель уровня жидкости в резервуаре: на входе постоянный расход притока, уровень — это интеграл расхода с заданным начальным значением. На выходе — текущий уровень.\r\n"},
            {"role": "assistant", "content": "\r\nengee.create(\"tank_level\")\r\n\r\n# Постоянный приток\r\nengee.add_block(\"/Basic/Sources/Constant\", \"tank_level/Inflow\")\r\nengee.set_param!(\"tank_level/Inflow\", \"Value\" =\u003e 0.2)\r\n\r\n# Интегратор уровня: dLevel/dt = Inflow\r\nengee.add_block(\"/Basic/Continuous/Integrator\", \"tank_level/LevelInt\")\r\nengee.set_param!(\"tank_level/LevelInt\", \"InitialCondition\" =\u003e 1.0)\r\n\r\n# Выход уровня\r\nengee.add_block(\"/Basic/Ports \u0026 Subsystems/Out1\", \"tank_level/LevelOut\")\r\n\r\n# Соединения\r\nengee.add_line(\"Inflow/1\", \"LevelInt/1\")\r\nengee.add_line(\"LevelInt/1\", \"LevelOut/1\")\r\n\r\nengee.save(\"tank_level\", \"tank_level.engee\", force=true)\r\n"},

            {"role": "user", "content": "твоя текущая задача - составить скрипт по следующему от пользователя указанию: " + user_prompt},
        ]
        return messages

    # def main(self):
    #     """
    #     CAN BE DEPRECATED
    #     Gets user prompt, augmenting with context from db and return model response
    #     """
    #     user_prompt = str(input("Введите промпт:\n"))
    #
    #     context = self.get_contexts(user_prompt)
    #
    #     messages = self.get_messages(user_prompt, context)
    #
    #     response = self.__ollama_client.chat(
    #         model=self.__settings.ollama_model_name,
    #         messages=messages,
    #     )
    #
    #     print(response.message.content)

    def generate_script(self, user_prompt: str) -> str:
        context = self.__retriever.query_points(user_prompt)
        messages = self.get_messages(user_prompt, context)
        response = self.__ollama_client.chat(
            model=self.__settings.ollama_model_name,
            messages=messages,
            keep_alive=False,
        )

        return response.message.content
