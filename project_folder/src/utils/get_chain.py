import os

import openai
from dotenv import load_dotenv

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key


def get_chain(
    vectorstore,
    system_message_template,
    memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
    human_message_template="{question}",
    model="gpt-3.5-turbo",
    temperature=0.2,
):
    qa_chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(model=model, temperature=temperature),
        vectorstore.as_retriever(),
        memory=memory,
        verbose=True,
        combine_docs_chain_kwargs={
            "prompt": ChatPromptTemplate.from_messages(
                [system_message_template, human_message_template]
            )
        },
        rephrase_question=False,
    )

    return qa_chain


def pass_in_dataset(dataset_path: str, embeddings_model="text-embedding-ada-002"):
    # load data
    loader = UnstructuredFileLoader(dataset_path)

    # split text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    texts = loader.load_and_split(text_splitter)

    # Load Data to vectorstore
    embeddings = OpenAIEmbeddings(model=embeddings_model)
    vectorstore = Chroma.from_documents(texts, embeddings)

    return vectorstore
