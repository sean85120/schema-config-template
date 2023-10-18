from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from random import choice

from main import ChainCharacter


class AbstractConversationManager(ABC):
    def __init__(self, speakers=None) -> None:
        self.speakers = speakers or []
        self.current_speaker_index = 0

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
        self.host_start = False
        self.previous_response = None
        self.characters = [ChainCharacter(speaker) for speaker in speakers]

    def add_character(self, character_name):
        self.speakers.append(character_name)

    def remove_character(self, character_name):
        self.speakers.remove(character_name)

    def __iter__(self):
        return self

    def __next__(self, new_topic=None):
        if not self.speakers:
            raise StopIteration

        if not self.host_start:
            query = self.host_intro(news_topic=new_topic)
            self.host_start = True

        query = self.previous_response or query

        response = self.characters[self.current_speaker_index].response(query)

        self.previous_response = response

        self.current_speaker_index = (self.current_speaker_index + 1) % len(
            self.speakers
        )

        result = []
        result.append(query)
        result.append(response)

        return result

    def host_intro(
        self,
        news_topic,
        host_name="流口香",
    ):
        query = f"今日頭條: {news_topic}，請流口香主持人先簡述一次新聞，再邀請來賓柯文哲分享新聞的看法"
        host = ChainCharacter(host_name)
        host_response = host.response(query=query)

        return host_response

    def start_conversation(self):
        for _ in range(len(self.speakers)):
            speaker = self.speakers[self.current_speaker_index]
            self.current_speaker_index = (self.current_speaker_index + 1) % len(
                self.speakers
            )
            print(f"{speaker} is saying")


class JyanKen(AbstractConversationManager):
    def __init__(
        self, jyanken_status: bool = False, speakers: list = None, host: str = None
    ) -> None:
        super().__init__(speakers)
        self.speakers = speakers or []
        self.jyanken_status = jyanken_status

        self.host = host

        self.characters = [ChainCharacter(speaker) for speaker in speakers]

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

        draw_chats = {}
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

                # add character
                ## TODO: add comment while draw

                for index, character in enumerate(self.characters):
                    response = character.response(
                        query=f"上一局你出了{result[index]}，猜拳沒有勝負,，請問下一拳要出什麼，從剪刀石頭布裡選擇一種"
                    )
                    draw_chats[f"{character.character_name}"] = response

            print("draw_chats: ", draw_chats)

        winner_ken = self.determine_jyanken_winner(set(result))
        winner_indexes = [i for i, value in enumerate(result) if value == winner_ken]
        winners_list = [self.speakers[i] for i in winner_indexes]
        winners = ", ".join(winners_list)
        print(f"{winners} win!")


# if __name__ == "__main__":
#     speakers = ["柯文哲", "韓國瑜", "蔡英文", "宋楚瑜"]
#     jyanken = JyanKen(speakers=speakers)

#     print("status: ", jyanken.__dict__)

#     jyanken.run_jyanken_game()

if __name__ == "__main__":
    speakers = ["柯文哲", "韓國瑜", "蔡英文", "宋楚瑜"]
    news_topic = "台積電正式表態！放棄進駐龍科三期、將續與管理局配合另覓地建廠"
    conversation = Conversation(speakers=speakers)

    result = conversation.__next__(news_topic)
    print("result:", result)
