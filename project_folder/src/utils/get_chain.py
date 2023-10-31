import os
import threading
import uuid

import openai
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.schema.document import Document
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain.vectorstores import Chroma

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key


chroma_lock = threading.Lock()


def get_chain(
    vectorstore,
    system_message_template,
    memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
    human_message_template="{question}",
    model="gpt-3.5-turbo",
    temperature=0.2,
    top_k=1,
):
    qa_chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(model=model, temperature=temperature),
        vectorstore.as_retriever(search_kwargs={"k": top_k}),
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


def pass_in_text_as_dataset(text: str, embeddings_model="text-embedding-ada-002"):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    docs = [Document(page_content=x) for x in text_splitter.split_text(text)]

    # Load Data to vectorstore
    embeddings = OpenAIEmbeddings(model=embeddings_model)

    with chroma_lock:
        vectorstore = Chroma.from_documents(
            docs, embeddings, collection_name=uuid.uuid4().hex
        )

    return vectorstore
