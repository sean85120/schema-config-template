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
        pass

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
        example_json_dict = chain_json_manager.load_example_chain_json()
        with open(self.get_chain_path(), "w") as f:
            f.write(json.dumps(example_json_dict, ensure_ascii=False))

        system_message = f"""
            Use the following pieces of context to answer the users question.
            If you don't know the answer, please make up something based on the following contexts.
            You are not a AI assitance, you are a human.
            (你是{character_name}，以{character_name}的身份，用繁體中文一次回答一個問題，在提到{character_name}時，用“我”替換)
            """
        system_message_template = (
            system_message
            + """
            \n----------------\n{context}
            """
        )

        return "create character successfully"

    def get_chain_path(self) -> str:
        return os.path.join(
            self._base_directory,
            self._get_chain_filename(self.character_name, self.model_date),
        )

    def load_chain_json(self) -> str:
        chain_path = self.get_chain_path()
        with open(chain_path) as ifile:
            return json.load(ifile)

    def save_chain_json(self) -> str:
        output_filepath = self.get_chain_path()
        chain_json_data = self.load_chain_json()
        logging.debug(f"saving chain model json: {output_filepath}")
        with open(output_filepath, "w") as f:
            if isinstance(chain_json_data, str):
                f.write(chain_json_data)
            else:  # assume json-serializable
                f.write(json.dumps(chain_json_data, ensure_ascii=False))
        return output_filepath

    # TODO: refactor load chain and implement this
    def load_chain(self) -> str:
        pass

    def serialize_chain_json(self) -> dict:
        chain_json_data = self.load_chain_json()
        # Serialize the attributes of the class into the chain JSON.
        for key, value in self.__dict__.items():
            chain_json_data[key] = value

        return chain_json_data

    def deserialize_chain_json(self) -> dict:
        chain_json_data = self.load_chain_json()
        # Deserialize the chain JSON into the appropriate attributes of the class.
        for key, value in chain_json_data.items():
            setattr(self, key, value)

        return self


if __name__ == "__main__":
    kp = ChainCharacter(character_name="柯文哲", model_date="2023-10-04")
    print("kp_object_original:", kp.__dict__)

    kp.create(model="ft:gpt-3.5-turbo-0613:aist::82bfmfPv")


print("ok--------------------------------------------------------------------")
