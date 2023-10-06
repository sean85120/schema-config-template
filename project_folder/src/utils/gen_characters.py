from datetime import datetime

from src.schemas.models import CharacterDescription, CharacterInit
from src.utils.fuzzy_match import calculate_levenshtein_distance, is_name_exist


def create_character(description: CharacterDescription) -> dict:
    character_name = description.name if description.name else None
    character_description = description.description

    if character_name:
        levenshtein_distance = calculate_levenshtein_distance(
            character_name, DATASET_PATH
        )
        # check character name exist
        name_exist = is_name_exist(levenshtein_distance)
    else:
        name_exist = False

    if not name_exist:
        gen_file = gen_character_dataset(character_description, DATASET_PATH)
        if gen_file:
            chain_json = init_character(CharacterInit(character_name=character_name))

            return {"name_exist": name_exist, "response": chain_json}

        else:
            return {"name_exist": name_exist, "response": "dataset gen error"}
    else:
        min_distance = min(levenshtein_distance)
        min_index = levenshtein_distance.index(min_distance)
        name = list_datasets(DATASET_PATH)[min_index]

        return {"name_exist": name_exist, "response": name}


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
