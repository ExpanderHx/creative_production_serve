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
        message = message,
        code = 1
    )


async def chat(
        question: str = Body(..., description="Question", example="填入问题"),
        history: List[List[str]] = Body(
            [],
        ),
):
    code = 0;
    resp = None;
    errMsg= "";
    try:
        if modelHandle is not None and modelHandle.load_model_handle is not None and modelHandle.load_model_handle.model is not None:
            for answer_result in modelHandle.generatorAnswer(prompt=question, history=history, streaming=True):
                resp = answer_result.llm_output["answer"]
                history = answer_result.history
                code = 1;
        else:
            errMsg = "模型还未加载，请先加载模型"
    except Exception as e:
        print(e)
        pass


    return ChatMessage(
        code=code,
        question=question,
        response=resp,
        history=history,
        source_documents=[],
        errMsg=errMsg
    )

async def reload_model(chatModelConfig: ChatModelConfig):
    code = 0;
    errMsg = "";
    try:
        modelConfig = ModelConfig.handle_dict(chatModelConfig.dict())
        global modelHandle;
        if modelHandle is None:
            modelHandle = ModelHandle(model_config);
        modelHandle.reload_model(modelConfig)
        code = 1;
    except Exception as e:
        errMsg = "模型加载失败，请重试"
        print(e)

    return responseModal(
        message = "模型已重新加载",
        code=code,
        errMsg=errMsg
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
    print('*----------------服务端启动完成------------------*')
    modelHandle = ModelHandle(model_config);
    # print(model_config.model_name)
    # print(model_config.tokenizer_name)
    # modelHandle.load_model();
    start_serve(host, port);