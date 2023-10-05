from datetime import datetime

from fuzzy_match import calculate_levenshtein_distance, is_name_exist
from main import chain_json_manager, retrieval_dataset_manager
from src.schemas.models import CharacterDescription, CharacterInit


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
