from typing import List

import pydantic
from pydantic import BaseModel


class ChatMessage(BaseModel):
    question: str = pydantic.Field(None, description="Question text")
    code: int = pydantic.Field(..., description="code")
    version: int = pydantic.Field(1, description="version")
    response: str = pydantic.Field(None, description="Response text")
    errMsg: str = pydantic.Field(None, description="errMsg")
    history: List[List[str]] = pydantic.Field(None, description="History text")
    source_documents: List[str] = pydantic.Field(
        ..., description="List of source documents and their scores"
    )

    class Config:
        schema_extra = {

        }