from typing import List

import pydantic
from pydantic import BaseModel


class responseModal(BaseModel):
    message: str = pydantic.Field(..., description="描述消息")

    class Config:
        schema_extra = {

        }