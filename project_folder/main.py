import openai
from dotenv import load_dotenv

load_dotenv()

import os

openai.api_key = os.getenv("OPENAI_API_KEY")

import json
import logging
import os
from collections import defaultdict
from typing import List

from settings import Config

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from langchain.prompts import SystemMessagePromptTemplate
from src.schemas.models import ChainVersion
from src.utils.get_chain import get_chain, pass_in_dataset


class DatasetManager:
    def __init__(self, base_directory=Config.DATASET_DIRECTORY):
        self._base_directory = base_directory

    def list_characters(self):
        raise NotImplementedError("Subclasses must implement this method")

    def load_dataset(self, character_name):
        raise NotImplementedError("Subclasses must implement this method")

    def add_to_dataset(self, character_name, new_data):
        raise NotImplementedError("Subclasses must implement this method")


class RetrievalDatasetManager(DatasetManager):
    RETRIEVAL_DATASETS_DIRECTORY_NAME = "retrieval_datasets"

    def __init__(self, base_directory=Config.DATASET_DIRECTORY):
        super().__init__(base_directory)
        self._DATASET_DIRECTORY = os.path.join(
            base_directory, self.RETRIEVAL_DATASETS_DIRECTORY_NAME
        )

    def list_characters(self) -> List[str]:
        return self.list_datasets(self._DATASET_DIRECTORY)

    def load_dataset(self, character_name) -> str:
        dataset_path = self.get_dataset_filepath(character_name)
        try:
            with open(dataset_path, "r") as f:
                return f.read()
        except Exception as e:
            print(f"ERROR: dataset does not exist at {dataset_path}")
            raise e

    def add_to_dataset(self, character_name, new_data) -> None:
        dataset_path = self.get_dataset_filepath(character_name)
        with open(dataset_path, "a") as f:
            f.write(new_data)

    def _get_dataset_filename(self, character_name) -> str:
        return f"{character_name}_dataset.txt"

    def get_dataset_filepath(self, character_name) -> str:
        return os.path.join(
            self._DATASET_DIRECTORY, self._get_dataset_filename(character_name)
        )

    def list_datasets(self, directory) -> List[str]:
        return [filename for filename in os.listdir(directory)]


class ChainJsonManager(DatasetManager):
    CHAIN_JSON_DIRECTORY_NAME = "chain_json"

    def __init__(self, base_directory=Config.DATASET_DIRECTORY):
        super().__init__(base_directory)
        self._base_directory = os.path.join(
            base_directory, self.CHAIN_JSON_DIRECTORY_NAME
        )

    # TODO: implement isCharacterExist get_latest_chain
    def isCharacterExist(self, character_name) -> bool:
        return character_name in self.list_characters()

    def get_latest_chain(self, character_name) -> str:
        chain_versions = self.list_characters_version()[character_name]
        chain_versions.sort()
        return chain_versions[-1]

    def list_characters(self):
        return self.list_characters_version().keys()

    def list_characters_version(self) -> dict:
        filenames = [
            filename.split(".")[0] for filename in os.listdir(self._base_directory)
        ]
        result = defaultdict(list)
        for name in filenames:
            character_name = name.split("_")[0]
            result[character_name].append(name)
        return result

    def _get_chain_filename(self, name, chain_version_date) -> str:
        return f"{name}_{chain_version_date}.json"

    def get_chain_path(self, character_name, model_date) -> str:
        return os.path.join(
            self._base_directory,
            self._get_chain_filename(character_name, model_date),
        )

    def save_chain_json(self, character_name, current_date, chain_json_data) -> str:
        output_filepath = self.get_chain_path(character_name, str(current_date))
        logging.debug(f"saving chain model json: {output_filepath}")
        with open(output_filepath, "w") as f:
            if isinstance(chain_json_data, str):
                f.write(chain_json_data)
            else:  # assume json-serializable
                f.write(json.dumps(chain_json_data, ensure_ascii=False))
        return output_filepath

    def load_example_chain_json(self, example_name="example") -> str:
        chain_path = os.path.join(self._base_directory, f"{example_name}.json")
        with open(chain_path) as ifile:
            return json.load(ifile)

    def load_chain_json(self, character_name, model_date) -> str:
        chain_path = self.get_chain_path(character_name, model_date)
        with open(chain_path) as ifile:
            return json.load(ifile)

    def serialize_chain_json(self, character_name, model_date) -> dict:
        chain_json_data = self.load_chain_json(character_name, model_date)
        # Serialize the attributes of the class into the chain JSON.
        for key, value in self.__dict__.items():
            chain_json_data[key] = value

        return chain_json_data

    def deserialize_chain_json(self, character_name, model_date) -> dict:
        chain_json_data = self.load_chain_json(character_name, model_date)
        # Deserialize the chain JSON into the appropriate attributes of the class.
        for key, value in chain_json_data.items():
            setattr(self, key, value)

        return self


# init
retrieval_dataset_manager = RetrievalDatasetManager()
chain_json_manager = ChainJsonManager()


class Character:
    def __init__(self, character_name, model_date):
        self.character_name = character_name
        self.model_date = model_date

    def create(self):
        pass

    def get_description(self):
        pass

    def get_version(self):
        pass

    def save_character(self):
        pass


class ChainCharacter(Character, ChainJsonManager):
    def __init__(
        self,
        character_name,
        model_date,
        _base_directory=os.path.join(Config.DATASET_DIRECTORY, "chain_json"),
    ):
        super().__init__(character_name, model_date)
        self.character_name = character_name
        self.model_date = model_date
        self._base_directory = _base_directory

    def create(self, model="gpt-3.5-turbo") -> None:
        character_name = self.character_name
        example_json_dict = self.load_example_chain_json()
        with open(self.get_chain_path(self.character_name, self.model_date), "w") as f:
            f.write(json.dumps(example_json_dict, ensure_ascii=False))

        system_message = f"""
            Use the following pieces of context to answer the users question.
            If you don't know the answer, please make up something based on the following contexts.
            You are not a AI assitance, you are a human.
            (你是{character_name}，以{character_name}的身份，用繁體中文一次回答一個問題，在提到{character_name}時，用“我”替換)
            """
        system_message_template = system_message + "\n----------------\n{context}"

        print("create character successfully")

    def get_latest_version(self) -> str:
        return super().get_latest_chain(self.character_name)

    def get_description(self):
        pass

    def get_version(self) -> ChainVersion:
        return f"{self.character_name}_{self.model_date}"

    def save_character(self) -> None:
        return self.save_chain_json(self.character_name, self.model_date, self.__dict__)

    def response(self, query) -> str:
        self.deserialize_chain_json(self.character_name, self.model_date)

        print("self_dict:", self.__dict__)
        chain_json_text = self.load_chain_json(self.character_name, self.model_date)
        retrieval_dataset_path = retrieval_dataset_manager.get_dataset_filepath(
            self.character_name
        )

        # load data to vectorstore
        embeddings_model = self.vectorstore["embeddings_model"]
        vectorstore = pass_in_dataset(retrieval_dataset_path, embeddings_model)

        system_message_template = SystemMessagePromptTemplate.from_template(
            chain_json_text["combine_docs_chain_kwargs"]["prompt"][
                "system_message_template"
            ]
        )

        qa_chain = get_chain(
            vectorstore=vectorstore,
            system_message_template=system_message_template,
            model=self.llm["model"],
            temperature=self.llm["temperature"],
        )

        default_prompt = str(
            self.combine_docs_chain_kwargs["prompt"]["default_prompt"]
        ).format(character_name=self.character_name)

        result = qa_chain(
            {
                "question": query + default_prompt,
                "chat_history": self.memory["chat_history"],
            }
        )

        # update chat history
        self.memory["chat_history"].append((query, result["answer"]))

        # save chain
        self.save_character()

        return result["answer"]


if __name__ == "__main__":
    kp = ChainCharacter(character_name="柯文哲", model_date="2023-10-04")
    print("kp_object_original:", kp.__dict__)

    # response = kp.response("你好")
    # print("response:", response)

    latest_version = kp.get_latest_version()
    print("latest_version:", latest_version)


print("ok--------------------------------------------------------------------")
