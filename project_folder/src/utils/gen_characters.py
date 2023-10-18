import os

import openai
from dotenv import load_dotenv
from src.schemas.models import CharacterDescription, CharacterInit
from src.utils.fuzzy_match import calculate_levenshtein_distance, is_name_exist

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key


def gen_character_dataset(character_name, description, dataset_path):
    print("start to generate character dataset")
    prompt = f"""
    第一，請生成一個角色{character_name} 是{description}
    第二，請生成這個角色會說的三十句台詞，
    並照以下格式回覆：

    角色:
    性別:
    職業:
    敘述:
    台詞:

    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "user", "content": prompt}],
    )
    dataset_file = f"{dataset_path}/{character_name}_dataset.txt"

    with open(dataset_file, "a") as file:
        file.write(response["choices"][0]["message"]["content"])

    return dataset_file


def gen_charcater_prompt_template(character_name, description) -> dict:
    system_message = f"""
    Use the following pieces of context to answer the users question.
    If you don't know the answer, please make up something based on the following contexts.
    You are not a AI assitance, you are a human.
    (你是{character_name}，以{character_name}的身份，用繁體中文一次回答一個問題，在提到{character_name}時，用“我”替換)
    """
    system_message_template = system_message + "\n----------------\n{context}"

    character_prompot_template = {
        "default_prompt": f"(你是{character_name} {description}。請你以20字回答問題，在提到{character_name}時，用“我”替換)",
        "human_message_template": "{question}",
        "system_message_template": system_message_template,
    }

    return character_prompot_template
