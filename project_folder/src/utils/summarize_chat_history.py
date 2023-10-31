import os

import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

from typing import List


def summarize_chat_history(chat_history: List[str]) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"please summarize the conversation below in one line in Traditional Chinese.\n\n ------------------{chat_history}------------------\n\n",
            },
        ],
    )["choices"][0]["message"]["content"]

    print("finish summarize_chat_history")

    print("response:", response)

    return response


if __name__ == "__main__":
    chat_history = """
    [
        ["柯郭合可能是柯文哲和郭台銘合作的一種方案，柯辦表示希望團結各方力量。我很期待聽聽郭董對此的看法。", "我怎麼當特使，我每天都忙得要死，我還要當特使，我根本沒有一天休息。\n\n" ],
        ["你說得對，當特使確實需要負責很多事情，但有時候也需要願意付出一些努力，才能達成更大的目標。", "你先把那三個方案打出來，我可以跟你討論一下\n"]

    ]
    """
    result = summarize_chat_history(chat_history)

    print("result:", result)
