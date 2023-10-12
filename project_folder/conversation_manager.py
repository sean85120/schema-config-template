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

    def start_janken(self):
        result = []
        for _ in range(len(self.speakers)):
            speaker = self.speakers[self.current_speaker_index]
            self.current_speaker_index = (self.current_speaker_index + 1) % len(
                self.speakers
            )
            # jyanken
            ken = ["r", "s", "p"]
            ken_choice = choice(ken)
            result.append(ken_choice)
            print(f"{speaker} choose {ken_choice}")
        return result

    def _is_jyanken_winner(self, combination):
        valid_combinations = {
            frozenset(["r", "s"]),
            frozenset(["s", "p"]),
            frozenset(["p", "r"]),
        }

        if frozenset(combination) in valid_combinations:
            pass

        return frozenset(combination) in valid_combinations

    def janken_result(self):
        i = 1
        while not self.jyanken_status:
            print("i:-------------------------------------------", i)

            result = self.start_janken()

            print("janken_result: ", result)

            counter = Counter(result)

            if len(counter) == 2:
                print("valid janken")
                self.jyanken_status = True
            else:
                i += 1
                print("invalid janken")

        combination = set(result)
        print("keys: ", combination)
        if self._is_jyanken_winner(combination):
            print("wins!")
        else:
            print("wrong!!")


# if __name__ == "__main__":
#     # Example usage:
#     speakers = ["Alice", "Bob", "Carol"]
#     conversation = Conversation(speakers)

#     conversation.add_character("Dave")
#     conversation.remove_character("Bob")

#     # conversation.start_conversation()
#     # print("conversation.speakers: ", conversation.speakers.__len__())

#     speaker = next(conversation)
#     print("speaker: ", speaker)

#     speaker2 = next(conversation)
#     print("speaker2: ", speaker2)

#     speaker3 = next(conversation)
#     print("speaker3: ", speaker3)


if __name__ == "__main__":
    speakers = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank"]
    jyanken = JyanKen(speakers=speakers)

    print("status: ", jyanken.__dict__)

    jyanken.janken_result()
