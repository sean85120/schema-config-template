# from abc import ABC, abstractmethod
# from collections import defaultdict


# class AbstractConversation(ABC):
#     def __init__(self, speakers=None, speaking_status=None) -> None:
#         self.speaking_status = speaking_status or defaultdict(str)
#         self.speakers = speakers or []

#     @abstractmethod
#     def add_character(self) -> None:
#         pass

#     @abstractmethod
#     def remove_character(self) -> None:
#         pass

#     @abstractmethod
#     def assign_character(self) -> None:
#         pass

#     @abstractmethod
#     def __iter__(self) -> None:
#         pass

#     @abstractmethod
#     def __next__(self) -> None:
#         pass


# class Conversation(AbstractConversation):
#     def __init__(self):
#         super().__init__()

#     def add_character(self, character_name: str) -> None:
#         self.speakers.append(character_name)

#     def remove_character(self, character_name: str) -> None:
#         if character_name in self.speakers:
#             self.speakers.remove(character_name)

#     def __iter__(self):
#         return self

#     def __next__(self):
#         if not self.speakers:
#             raise StopIteration
#         character = self.assign_character()
#         if character:
#             return character
#         else:
#             # If no one can speak, reset speaking_status and start over.
#             self.speaking_status = defaultdict(str)
#             return self.__next__()

#     def assign_character(self) -> None:
#         for character in self.speakers:
#             if not self.speaking_status.get(character, False):
#                 self.speaking_status[character] = True
#                 return character

#     def start_conversation(self):
#         speaker_order = self.__iter__()
#         speaker_order.__next__()
#         print()


# if __name__ == "__main__":
#     conversation_loop = Conversation()
#     conversation_loop.add_character("Alice")
#     conversation_loop.add_character("Bob")
#     conversation_loop.add_character("Carol")

#     conversation_loop.start_conversation()


from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from random import choice

from main import ChainCharacter


class AbstractConversationManager(ABC):
    def __init__(self, speakers=None) -> None:
        self.speakers = speakers or []  # Initialize with an empty list of speakers
        self.current_speaker_index = 0  # Initialize the current speaker

    @abstractmethod
    def add_character(self, character_name):
        pass

    @abstractmethod
    def remove_character(self, character_name):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self):
        pass


class Conversation(AbstractConversationManager):
    def __init__(self, speakers):
        super().__init__(speakers)
        self.current_speaker_index = 0

    def add_character(self, character_name):
        self.speakers.append(character_name)

    def remove_character(self, character_name):
        self.speakers.remove(character_name)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.speakers:
            raise StopIteration
        speaker = self.speakers[self.current_speaker_index]
        self.current_speaker_index = (self.current_speaker_index + 1) % len(
            self.speakers
        )
        return speaker

    def start_conversation(self):
        for _ in range(len(self.speakers)):
            speaker = self.speakers[self.current_speaker_index]
            self.current_speaker_index = (self.current_speaker_index + 1) % len(
                self.speakers
            )
            print(f"{speaker} is saying")


class JyanKen(AbstractConversationManager):
    def __init__(self, jyanken_status: bool = False, speakers: list = None) -> None:
        super().__init__(speakers)
        self.speakers = speakers or []
        self.jyanken_status = jyanken_status

    def add_character(self, character_name) -> None:
        self.speakers.append(character_name)

    def remove_character(self, character_name) -> None:
        self.speakers.remove(character_name)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.speakers:
            raise StopIteration
        speaker = self.speakers[self.current_speaker_index]
        self.current_speaker_index = (self.current_speaker_index + 1) % len(
            self.speakers
        )
        return speaker

    def play_jyanken_round(self) -> list:
        result = []
        for _ in range(len(self.speakers)):
            speaker = self.speakers[self.current_speaker_index]
            self.current_speaker_index = (self.current_speaker_index + 1) % len(
                self.speakers
            )
            # jyanken
            ken = ["rock", "scissors", "paper"]
            ken_choice = choice(ken)
            result.append(ken_choice)
            print(f"{speaker} chooses {ken_choice}")
        return result

    def determine_jyanken_winner(self, result: list) -> str:
        combinations = set(result)
        winner_combinations = {
            frozenset(["rock", "scissors"]): "rock",
            frozenset(["scissors", "paper"]): "scissors",
            frozenset(["paper", "rock"]): "paper",
        }

        for combination, winner in winner_combinations.items():
            if combinations == combination:
                return winner

    def run_jyanken_game(self) -> str:
        i = 1
        while not self.jyanken_status:
            print("i:-------------------------------------------", i)

            result = self.play_jyanken_round()

            print("janken_result: ", result)

            counter = Counter(result)

            if len(counter) == 2:
                print("valid janken")
                self.jyanken_status = True
            else:
                i += 1
                print("invalid janken")

        winner_ken = self.determine_jyanken_winner(set(result))
        winner_indexes = [i for i, value in enumerate(result) if value == winner_ken]
        winners_list = [self.speakers[i] for i in winner_indexes]
        winners = ", ".join(winners_list)
        print(f"{winners} win!")


if __name__ == "__main__":
    speakers = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank"]
    jyanken = JyanKen(speakers=speakers)

    print("status: ", jyanken.__dict__)

    jyanken.run_jyanken_game()
