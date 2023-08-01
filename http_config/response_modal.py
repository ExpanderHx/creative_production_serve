from typing import List

import pydantic
from pydantic import BaseModel


class responseModal(BaseModel):
    message: str = pydantic.Field(..., description="描述消息")
    code: int = pydantic.Field(..., description="code")
    version: int = pydantic.Field(1, description="version")
    errMsg: str = pydantic.Field(None, description="errMsg")

    class Config:
        schema_extra = {

        }