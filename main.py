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
        self._CHAIN_JSON_DIRECTORY = os.path.join(
            base_directory, self.CHAIN_JSON_DIRECTORY_NAME
        )

    def list_characters_version(self) -> dict:
        filenames = [
            filename.split(".")[0]
            for filename in os.listdir(self._CHAIN_JSON_DIRECTORY)
        ]
        result = defaultdict(list)
        for name in filenames:
            character_name = name.split("_")[0]
            result[character_name].append(name)
        return result

    def _get_chain_filename(self, name, chain_version_date) -> str:
        return f"{name}_{chain_version_date}.json"

    def get_chain_path(self, name, chain_version_date) -> str:
        return os.path.join(
            self._CHAIN_JSON_DIRECTORY,
            self._get_chain_filename(name, chain_version_date),
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
        chain_path = os.path.join(self._CHAIN_JSON_DIRECTORY, f"{example_name}.json")
        with open(chain_path) as ifile:
            return json.load(ifile)

    def load_chain_json(self, character_name, model_date) -> str:
        chain_path = self.get_chain_path(character_name, model_date)
        with open(chain_path) as ifile:
            return json.load(ifile)


# init
retrieval_dataset_manager = RetrievalDatasetManager()
chain_json_manager = ChainJsonManager()


class CharacterManager(
    ChainJsonManager,
):
    def __init__(
        self,
        _CHAIN_JSON_DIRECTORY,
        character_name,
        model_date,
        model,
        default_prompt,
    ):
        super().__init__(_CHAIN_JSON_DIRECTORY)
        self.character_name = character_name
        self.model_date = model_date
        self.model = model
        self.default_prompt = default_prompt

    def get_chain_path(self) -> str:
        return super().get_chain_path(self.character_name, self.model_date)

    def save_chain_json(self) -> str:
        return super().save_chain_json(self.character_name, self.model_date)

    # TODO: refactor load chain and implement this
    def load_chain(self) -> str:
        pass

    def serialize_chain_json(self) -> dict:
        pass

    def deserialize_chain_json(self, chain_json) -> dict:
        # Deserialize the chain JSON into the appropriate attributes of the class.
        self.character_name = chain_json.get("llm", {}).get("model", "")
        self.model_date = ""  # You can extract this from the chain_json if it's present
        self.model = chain_json.get("llm", {}).get("model", "")
        self.default_prompt = ""


if __name__ == "__main__":
    kp = CharacterManager(
        "柯文哲", "2023-10-02", "ft:gpt-3.5-turbo-0613:aist::82bfmfPv", "prompt"
    )

    kp_chain_path = kp.get_chain_path()

    print(kp_chain_path)


print("ok--------------------------------------------------------------------")
