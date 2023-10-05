from typing import List, Optional

from pydantic import BaseModel, Field


class CharacterDescription(BaseModel):
    name: Optional[str]
    description: str


class ChainVersion(BaseModel):
    name: str
    date: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")


class ChainLoad(BaseModel):
    chain_version: ChainVersion
    model: Optional[str] = "gpt-3.5-turbo"
    query: Optional[str] = None
    prompt: Optional[str] = None


class LoadOutput(BaseModel):
    speaker: str
    response: str


class CharacterInit(BaseModel):
    character_name: str
    model: Optional[str] = "gpt-3.5-turbo"


class AssignInput(BaseModel):
    chain_version: ChainVersion
    active_characters: Optional[list] = None
    query: Optional[str] = None


class AssignOutput(BaseModel):
    speaker: str
    assignee: str
    response: str
    wav_url: str
    ipa_timestamp: list


class ScriptInput(BaseModel):
    chain_version: ChainVersion
    query: Optional[str] = None
    speaking_lines: Optional[int] = 4
