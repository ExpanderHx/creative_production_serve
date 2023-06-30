
import pydantic
import uvicorn
from fastapi import FastAPI, Body
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

from model_handle.model_handle import ModelHandle
import os

# 是否开启跨域，默认为False，如果需要开启，请设置为True
# is open cross domain
OPEN_CROSS_DOMAIN = False

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

async def service_state(chatModelConfig: ChatModelConfig):
    modelConfig = ModelConfig.handle_dict(chatModelConfig.dict())
    modelHandle.reload_model(modelConfig)

    message= f'{"system_version":{system_version},"message":"服务端状态正常","state":200}'
    return responseModal(
        message = message
    )


async def chat(
        question: str = Body(..., description="Question", example="工伤保险是什么？"),
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
    modelHandle.reload_model(modelConfig)

    return responseModal(
        message = "模型已重新加载"
    )



def start_serve(host,port):
    global app

    app = FastAPI()
    if OPEN_CROSS_DOMAIN:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.get("/", response_model=BaseResponse)(document)
    app.post("/chat", response_model=ChatMessage)(chat)
    app.post("/reload_model", response_model=responseModal)(reload_model)

    uvicorn.run(app, host=host, port=port)

def getEnviron():
    # 使用os.environ获取环境变量字典，environ是在os.py中定义的一个dict environ = {}

    # Access all environment variables
    print('*---------------ENVIRON-------------------*')
    print(os.environ["HF_HOME"])
    # print(os.environ)
    print('*----------------HOME------------------*')




if __name__ == "__main__":
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=10800)

    args = vars(parser.parse_args())
    host = args.pop("host")
    port = args.pop("port")
    global modelHandle;
    getEnviron();
    model_config = ModelConfig.handle_dict(args)
    print('*----------------模型加载完成------------------*')
    modelHandle = ModelHandle(model_config);
    print(model_config.model_name)
    print(model_config.tokenizer_name)
    modelHandle.load_model();
    start_serve(host, port);