import logging
import os
import platform
import subprocess

import torch
import uvicorn


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



def set_env_dir(file_name,target_dir_path):
    """
    功能: 给Windows系统添加环境变量, Windows系统版本不能太低, 要支持软链接
    :param target_dir_path: 目标文件夹路径, 就是要添加到环境变量的文件夹路径
    :return:
    """

    # 创建一个bat文件, 来跑命令
    bat_file_path = os.path.join(os.getcwd(), "set_windows_env.bat")
    cmd_str = "mklink /d  C:\windows\{}  {}\n".format(file_name, target_dir_path)
    with open(bat_file_path, "w") as f:
        # 首先要获取管理员权限
        f.write(get_administrator_rights_cmd_str)
        f.write(cmd_str)

    subprocess.run(bat_file_path, shell=True)


def addGccPath():
    sys = platform.system()
    if sys == "Windows":
        print("OS is Windows!!!")
        # win cpu环境需要gcc编译
        if not torch.cuda.is_available():
            extractallW64devkit()

            dir_path = os.path.dirname(os.path.abspath(__file__))
            if "PATH" in os.environ:
                os.environ["PATH"] = os.environ["PATH"] + "; " + os.path.join(dir_path,'reliance','w64devkit')
                os.environ["PATH"] = os.environ["PATH"] + "; " + os.path.join(dir_path,'reliance','w64devkit', 'bin')
                set_env_dir('w64devkit',os.path.join(dir_path,'reliance','w64devkit'))
                # set_env(os.path.join(dir_path,'reliance','w64devkit', 'bin'))



# 不记录uvicorn日志
def uvicornUnLog():
    # 创建一个日志记录器
    logger = logging.getLogger("uvicorn")
    # 设置日志级别为DEBUG
    logger.setLevel(logging.DEBUG)

    # 创建一个过滤器，用于过滤特定路径的日志
    class ExcludePathFilter(logging.Filter):
        def __init__(self, excluded_paths):
            super().__init__()
            self.excluded_paths = excluded_paths

        def filter(self, record):
            # 获取请求路径
            request_path = uvicorn.RequestInfo.from_record(record).path
            # 检查请求路径是否在排除列表中
            return request_path not in self.excluded_paths

    # 添加过滤器到日志记录器
    exclude_filter = ExcludePathFilter(["/service_state"])
    logger.addFilter(exclude_filter)
