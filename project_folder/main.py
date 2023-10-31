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

from settings.settings import Config

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from datetime import datetime
from pathlib import Path

from langchain.callbacks import get_openai_callback
from langchain.prompts import SystemMessagePromptTemplate
from src.schemas.models import ChainVersion
from src.utils.gen_characters import (
    gen_character_dataset,
    gen_charcater_prompt_template,
)
from src.utils.get_chain import get_chain, pass_in_dataset, pass_in_text_as_dataset
from src.utils.summarize_chat_history import summarize_chat_history


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
            with open(dataset_path) as f:
                return json.load(f)
        except Exception as e:
            print(f"ERROR: dataset does not exist at {dataset_path}")
            raise e

    def add_to_dataset(self, character_name, new_data) -> None:
        dataset_path = self.get_dataset_filepath(character_name)
        with open(dataset_path, "a") as f:
            f.write(new_data)

    def _get_dataset_filename(self, character_name) -> str:
        return f"{character_name}_dataset.json"

    def get_dataset_filepath(self, character_name) -> str:
        filename = self._get_dataset_filename(character_name)
        if not filename in self.list_characters():
            raise FileNotFoundError(
                f"No dataset found for character '{character_name}'."
            )
        return os.path.join(self._DATASET_DIRECTORY, filename)

    def list_datasets(self, directory) -> List[str]:
        return [filename for filename in os.listdir(directory)]

    def gen_dataset(self, character_name, description):
        return gen_character_dataset(
            character_name, description, self._DATASET_DIRECTORY
        )


class ChainJsonManager(DatasetManager):
    CHAIN_JSON_DIRECTORY_NAME = "chain_json"

    def __init__(self, base_directory=Config.DATASET_DIRECTORY):
        super().__init__(base_directory)
        self._base_directory = os.path.join(
            base_directory, self.CHAIN_JSON_DIRECTORY_NAME
        )

    def _is_character_exist(self, character_name) -> bool:
        return character_name in self.list_characters()

    def _is_chain_version_exist(self, character_name, model_date) -> bool:
        version_str = f"{character_name}_{model_date}"

        if version_str in self.list_characters_version()[character_name]:
            return True

        else:
            return False

    def _create_empty_chain_file(self, character_name, current_date):
        output_filepath = os.path.join(
            self._base_directory,
            self._get_chain_filename(character_name, current_date),
        )
        with open(output_filepath, "w") as f:
            pass

    def get_latest_chain(self, character_name) -> str:
        chain_versions = self.list_characters_version().get(character_name, [])
        if not chain_versions:
            raise FileNotFoundError(
                f"No chain version found for character '{character_name}'."
            )

        sorted_chain_versions = sorted(chain_versions)
        return sorted_chain_versions[-1]

    # def list_characters(self) -> List[str]:
    #     return self.list_characters_version().keys()

    def list_characters_version(self) -> dict:
        filenames = [
            filename.split(".")[0] for filename in os.listdir(self._base_directory)
        ]
        result = defaultdict(list)
        for name in filenames:
            character_name = name.split("_")[0]
            result[character_name].append(name)
        return result

    def _get_chain_filename(self, charcater_name, model_date) -> str:
        return f"{charcater_name}_{model_date}.json"

    def get_chain_path(self, character_name, model_date) -> str:
        chain_path = os.path.join(
            self._base_directory,
            self._get_chain_filename(character_name, model_date),
        )

        if self._is_chain_version_exist(character_name, model_date):
            return chain_path
        else:
            raise FileNotFoundError(
                f"No chain version found for character '{character_name}_{model_date}'."
            )

    def save_chain_json(self, character_name, current_date, chain_json_data) -> str:
        if not self._is_chain_version_exist(character_name, current_date):
            self._create_empty_chain_file(character_name, current_date)

        output_filepath = self.get_chain_path(character_name, str(current_date))
        logging.debug(f"saving chain model json: {output_filepath}")
        with open(output_filepath, "w") as f:
            if isinstance(chain_json_data, str):
                f.write(chain_json_data)
            else:  # assume json-serializable
                json.dump(chain_json_data, f, ensure_ascii=False)
        return output_filepath

    def load_example_chain_json(self, example_name="example") -> str:
        chain_path = os.path.join(self._base_directory, f"{example_name}.json")
        with open(chain_path) as f:
            return json.load(f)

    def load_chain_json(self, character_name, model_date) -> str:
        chain_path = self.get_chain_path(character_name, model_date)
        try:
            with open(chain_path) as f:
                return json.load(f)

        except FileNotFoundError:
            print("the chain json file does not exist")

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

    def get_background(self):
        pass

    def get_versions(self):
        pass

    def save_character(self):
        pass


class ChainCharacter(Character, ChainJsonManager):
    def __init__(
        self,
        character_name,
        model_date=datetime.today().date().strftime("%Y-%m-%d"),
        _base_directory=os.path.join(Config.DATASET_DIRECTORY, "chain_json"),
        llm_model="gpt-3.5-turbo",
        top_k=1,
    ):
        super().__init__(character_name, model_date)
        self.character_name = character_name
        self.model_date = model_date
        self._base_directory = _base_directory
        if not self._is_chain_version_exist(self.character_name, self.model_date):
            self.create(model=llm_model)
        self.deserialize_chain_json(self.character_name, self.model_date)
        self.top_k = top_k

    def get_latest_version(self) -> str:
        return self.get_latest_chain(self.character_name)

    def get_versions(self) -> ChainVersion:
        return self.list_characters_version()[self.character_name]

    def get_description(self) -> str:
        chain_json_data = self.load_chain_json(self.character_name, self.model_date)

        return chain_json_data["description"]

    def create(self, description=None, model="gpt-3.5-turbo") -> str:
        character_files_path = retrieval_dataset_manager.list_characters()
        is_not_found = all(
            f"{self.character_name}_dataset.json" not in path
            for path in character_files_path
        )

        if is_not_found:
            retrieval_dataset_manager.gen_dataset(self.character_name, description)

        self.create_version(model=model)

    def create_version(self, model) -> str:
        character_name = self.character_name

        example_json_dict = self.load_example_chain_json()
        dataset = retrieval_dataset_manager.load_dataset(character_name)
        description = dataset["description"]

        # Generate the prompt template
        prompt_template = gen_charcater_prompt_template(
            self.character_name, description
        )

        # Update the example JSON dictionary
        example_json_dict.update(
            {
                "character_name": character_name,
                "model_date": self.model_date,
                "description": description,
                "combine_docs_chain_kwargs": {"prompt": prompt_template},
                "llm": {"model": model, "temperature": 0.8},
                "vectorstore": {
                    "background": dataset["dialogue"],
                    "embeddings_model": "text-embedding-ada-002",
                },
            }
        )

        self.save_chain_json(character_name, self.model_date, example_json_dict)
        self.deserialize_chain_json(self.character_name, self.model_date)

        return f"{character_name}_{self.model_date}"

    def save_character(self) -> str:
        ret = self.save_chain_json(self.character_name, self.model_date, self.__dict__)
        self.deserialize_chain_json(self.character_name, self.model_date)
        return ret

    def add_background(self, input: str) -> None:
        chain_json_data = self.load_chain_json(self.character_name, self.model_date)
        updated_background = chain_json_data["vectorstore"]["background"] + input
        chain_json_data.update(
            {
                "vectorstore": {
                    "background": updated_background,
                    "embeddings_model": "text-embedding-ada-002",
                },
            }
        )

        self.save_chain_json(self.character_name, self.model_date, chain_json_data)
        self.deserialize_chain_json(self.character_name, self.model_date)

    def set_prompt(self, system_message: str = None, user_message: str = None) -> None:
        chain_json_data = self.load_chain_json(self.character_name, self.model_date)

        system_prompt = (
            "\nUse the following pieces of context to answer the users question.\nIf you don't know the answer, please make up something based on the following contexts.\nYou are not a AI assitance, you are a human.\n"
            + system_message
            + "\n\n----------------\n{context}\n"
        )

        user_prompt = f"({user_message})"

        chain_json_data.update(
            {
                "combine_docs_chain_kwargs": {
                    "prompt": {
                        "system_message_template": system_prompt,
                        "human_message_template": "{question}",
                        "user_message_template": user_prompt,
                    }
                }
            }
        )

    def set_response(self, query: str, charcater_response: str, model=None) -> str:
        if not self._is_chain_version_exist(self.character_name, self.model_date):
            self.create_version(model=model)
        # Deserialize the chain JSON
        self.deserialize_chain_json(self.character_name, self.model_date)

        self.memory["chat_history"].append((query, charcater_response))

        # Save the character
        self.save_character()

        return charcater_response

    def fake_name_parser(self, response: str) -> str:
        name_to_replace = {
            "柯文哲": "柯批",
            "郭台銘": "我姓郭",
            "賴清德": "阿德",
            "侯友宜": "侯侯睏",
        }
        removed_real_name_response = response
        for real_name, fake_name in name_to_replace.items():
            removed_real_name_response = removed_real_name_response.replace(
                real_name, fake_name
            )
        return removed_real_name_response

    # #
    def _get_qa_chain(self, model=None, memory=None):
        if not self._is_chain_version_exist(self.character_name, self.model_date):
            self.create_version(model=model)
        # Deserialize the chain JSON
        self.deserialize_chain_json(self.character_name, self.model_date)

        # Load data to vector store
        vectorstore = pass_in_text_as_dataset(
            self.vectorstore["background"],
            self.vectorstore["embeddings_model"],
        )
        system_message_template = SystemMessagePromptTemplate.from_template(
            self.combine_docs_chain_kwargs["prompt"]["system_message_template"]
        )

        params = {
            "vectorstore": vectorstore,
            "system_message_template": system_message_template,
            "model": model if model else self.llm["model"],
            "temperature": self.llm["temperature"],
            "top_k": self.top_k,
        }

        if memory:
            params["memory"] = memory

        qa_chain = get_chain(**params)

        return qa_chain

    def response(self, query, model=None, prompt=None, memory=None) -> str:
        qa_chain = self._get_qa_chain(model=model, memory=memory)

        prompt = (
            str(self.combine_docs_chain_kwargs["prompt"]["default_prompt"])
            if not prompt
            else prompt
        )

        # Perform the query and get the result

        with get_openai_callback() as cb:
            result = qa_chain(
                {
                    "question": query + prompt,
                    "chat_history": self.memory["chat_history"],
                }
            )

            print("cb:", cb)
            print("prompt:", cb.prompt_tokens)
            print("completion:", cb.completion_tokens)
            print("total:", cb.total_tokens)
            print("cost:", cb.total_cost)

        removed_real_name_response = self.fake_name_parser(result["answer"])

        # Update chat history
        self.memory["chat_history"].append((query, removed_real_name_response))

        # summarize chat_history and add to every 3 rounds
        if len(self.memory["chat_history"]) > 3:
            print("summarized_memory")
            summarized_memory = summarize_chat_history(self.memory["chat_history"])

            self.add_background(summarized_memory)
            self.memory["chat_history"] = []

        # Save the character
        self.save_character()

        return removed_real_name_response


if __name__ == "__main__":
    kp = ChainCharacter(character_name="柯文哲")
    print("kp_object_original:", kp.__dict__)

    kp.create_version(model="ft:gpt-3.5-turbo-0613:aist::82bfmfPv")

    response = kp.response("你好")
    print("response:", response)


print("ok--------------------------------------------------------------------")
