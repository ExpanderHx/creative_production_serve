from typing import Optional

import pydantic
from pydantic import BaseModel


class ChatModelConfig(BaseModel):
    model_name: str = pydantic.Field(..., description="模型名称")
    tokenizer_name: str = pydantic.Field(..., description="tokenizer_name")
    load_device: Optional[str] = pydantic.Field(..., description="模型加载在哪个设备,默认cuda")
    history_len: int = pydantic.Field(..., description="历史长度")
    max_token: int = pydantic.Field(..., description="最大token数量")
    temperature: float = pydantic.Field(..., description="温度")
    top_p: float = pydantic.Field(..., description="返回查询的数量 知识问答时使用")
