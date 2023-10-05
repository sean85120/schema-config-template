import os

import Levenshtein


def list_datasets(file_path):
    return [name.split("_")[0] for name in os.listdir(file_path)]


def calculate_levenshtein_distance(query: str, file_path: str):
    filenames = list_datasets(file_path)

    levenshtein_distance = []
    for name in filenames:
        levenshtein_distance.append(Levenshtein.distance(query, name))

    return levenshtein_distance


def is_name_exist(levenshtein_distance: list):
    list_len = len(levenshtein_distance)
    name_exist = [0] * list_len
    for index, distance in enumerate(levenshtein_distance):
        name_exist[index] = True if distance <= 1 else False

    return False if name_exist == [False] * list_len else True


if __name__ == "__main__":
    is_name_exist("科文折", "../../retrieval_datasets/")
