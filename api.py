import platform
import subprocess
import sys
import zipfile

import pydantic
import torch
import uvicorn
from fastapi import FastAPI, Body, Request
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from chat.chat_message import ChatMessage
from config.args import parser
from config.model_config import ModelConfig
from config.system_config import system_version
from http_config.chat_model_config import ChatModelConfig
from http_config.response_modal import responseModal
from load_model_handle.load_model_handle import LoadModelHandle
from typing import List, Optional
import logging
from fastapi.responses import JSONResponse

from model_handle.model_handle import ModelHandle
import os
import logging

from util.start_util import addGccPath, getEnviron

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

# 是否开启跨域，默认为False，如果需要开启，请设置为True
# is open cross domain
OPEN_CROSS_DOMAIN = False


app = FastAPI()

# 创建一个日志记录器
logger = logging.getLogger("uvicorn")

# 创建一个请求钩子来取消特定路径的日志记录
# @app.middleware("http")
# async def exclude_path_middleware(request: Request, call_next):
#     if request.url.path == "/service_state":
#         # 临时禁用日志记录器
#         logger.disabled = True
#         try:
#             # 直接返回响应结果给客户端，不触发日志记录
#             message = f'{{"system_version":{system_version},"message":"服务端状态正常","state":200}}'
#             return  JSONResponse(message)
#         finally:
#             pass
#             # 恢复日志记录器
#             logger.disabled = False
#
#     else:
#         # 执行下一个中间件和路由处理程序
#         response = await call_next(request)
#         return response

class BaseResponse(BaseModel):
    code: int = pydantic.Field(200, description="HTTP status code")
    msg: str = pydantic.Field("success", description="HTTP status message")

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
            }
        }

async def document():
    return RedirectResponse(url="/docs")

async def service_state():
    message= f'{{"system_version":{system_version},"message":"服务端状态正常","state":200}}'
    return responseModal(
        message = message
    )


async def chat(
        question: str = Body(..., description="Question", example="填入问题"),
        history: List[List[str]] = Body(
            [],
        ),
):
    for answer_result in modelHandle.generatorAnswer(prompt=question, history=history,
                                                          streaming=True):
        resp = answer_result.llm_output["answer"]
        history = answer_result.history
        pass

    return ChatMessage(
        question=question,
        response=resp,
        history=history,
        source_documents=[],
    )

async def reload_model(chatModelConfig: ChatModelConfig):
    modelConfig = ModelConfig.handle_dict(chatModelConfig.dict())
    global modelHandle;
    if modelHandle is None:
        modelHandle = ModelHandle(model_config);
    modelHandle.reload_model(modelConfig)

    return responseModal(
        message = "模型已重新加载"
    )



def start_serve(host,port):
    global app
    if OPEN_CROSS_DOMAIN:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.get("/", response_model=BaseResponse)(document)
    app.post("/service_state", response_model=responseModal)(service_state)
    app.post("/chat", response_model=ChatMessage)(chat)
    app.post("/reload_model", response_model=responseModal)(reload_model)

    uvicorn.run(app, host=host, port=port)



if __name__ == "__main__":
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=10800)

    addGccPath();
    args = vars(parser.parse_args())
    host = args.pop("host")
    port = args.pop("port")
    global modelHandle;
    getEnviron();
    model_config = ModelConfig.handle_dict(args)
    print('*----------------模型加载完成------------------*')
    modelHandle = ModelHandle(model_config);
    # print(model_config.model_name)
    # print(model_config.tokenizer_name)
    # modelHandle.load_model();
    start_serve(host, port);