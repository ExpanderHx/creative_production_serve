import subprocess
import sys
import zipfile

import pydantic
import torch
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
    app.post("/service_state", response_model=responseModal)(service_state)
    app.post("/chat", response_model=ChatMessage)(chat)
    app.post("/reload_model", response_model=responseModal)(reload_model)

    uvicorn.run(app, host=host, port=port)

def getEnviron():
    # 使用os.environ获取环境变量字典，environ是在os.py中定义的一个dict environ = {}

    # Access all environment variables
    print('*---------------ENVIRON-------------------*')
    if "HF_HOME" in os.environ:
        print(os.environ["HF_HOME"])
    # print(os.environ)
    print('*----------------HOME------------------*')


def extractallW64devkit():
    try:
        dir_path = os.path.dirname(os.path.abspath(__file__))
        # 压缩文件路径
        zip_path = os.path.join(dir_path,'reliance','w64devkit.zip')
        # 文件存储路径
        save_path = os.path.join(dir_path,'reliance')

        # 读取压缩文件
        file = zipfile.ZipFile(zip_path)
        # 解压文件
        print('开始解压...')
        file.extractall(save_path)
        print('解压结束。')
        # 关闭文件流
        file.close()
    except Exception as r:
        print(print('异常 %s' %(r)))


get_administrator_rights_cmd_str = """
@echo off
CLS
:init
setlocal DisableDelayedExpansion
set "batchPath=%~0"
for %%k in (%0) do set batchName=%%~nk
set "vbsGetPrivileges=%temp%\OEgetPriv_%batchName%.vbs"
setlocal EnableDelayedExpansion
:checkPrivileges
NET FILE 1>NUL 2>NUL
if '%errorlevel%' == '0' ( goto gotPrivileges ) else ( goto getPrivileges )
:getPrivileges
if '%1'=='ELEV' (echo ELEV & shift /1 & goto gotPrivileges)
ECHO Set UAC = CreateObject^("Shell.Application"^) > "%vbsGetPrivileges%"
ECHO args = "ELEV " >> "%vbsGetPrivileges%"
ECHO For Each strArg in WScript.Arguments >> "%vbsGetPrivileges%"
ECHO args = args ^& strArg ^& " " >> "%vbsGetPrivileges%"
ECHO Next >> "%vbsGetPrivileges%"
ECHO UAC.ShellExecute "!batchPath!", args, "", "runas", 1 >> "%vbsGetPrivileges%"
"%SystemRoot%\System32\WScript.exe" "%vbsGetPrivileges%" %*
exit /B
:gotPrivileges
setlocal & pushd .
cd /d %~dp0
if '%1'=='ELEV' (del "%vbsGetPrivileges%" 1>nul 2>nul & shift /1)
"""


def set_env(target_dir_path):
    """
    功能: 给Windows系统添加环境变量, Windows系统版本不能太低, 要支持软链接
    :param target_dir_path: 目标文件夹路径, 就是要添加到环境变量的文件夹路径
    :return:
    """

    # 创建一个bat文件, 来跑命令
    bat_file_path = os.path.join(os.getcwd(), "set_windows_env.bat")

    with open(bat_file_path, "w") as f:
        # 首先要获取管理员权限
        f.write(get_administrator_rights_cmd_str)

        for file_name in os.listdir(target_dir_path):
            file_path = os.path.join(target_dir_path, file_name)

            if os.path.isdir(file_path):
                # 是文件夹, 那么就创建文件夹的软链接
                cmd_str = "mklink /d  C:\windows\{}  {}\n".format(file_name, file_path)

            elif os.path.isfile(file_path):
                # 是文件, 那么就创建文件的软链接
                cmd_str = "mklink  C:\windows\{}  {}\n".format(file_name, file_path)

            f.write(cmd_str)

    subprocess.run(bat_file_path, shell=True)


def addGccPath():
    # win cpu环境需要gcc编译
    if not torch.cuda.is_available():
        extractallW64devkit()

        dir_path = os.path.dirname(os.path.abspath(__file__))
        if "PATH" in os.environ:
            os.environ["PATH"] = os.environ["PATH"] + "; " + os.path.join(dir_path,'reliance','w64devkit')
            os.environ["PATH"] = os.environ["PATH"] + "; " + os.path.join(dir_path,'reliance','w64devkit', 'bin')
            set_env(os.path.join(dir_path,'reliance','w64devkit'))
            set_env(os.path.join(dir_path,'reliance','w64devkit', 'bin'))





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