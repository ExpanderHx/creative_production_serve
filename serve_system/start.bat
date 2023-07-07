@echo off
chcp 65001


cd /d %~dp0
set "WINPYDIR=%~dp0\python\python-3.9-win"
echo  %~dp0


IF EXIST %WINPYDIR% (
    echo 检测到内置集成环境，使用内置Python解释器
    set "PATH=%WINPYDIR%\;%WINPYDIR%\DLLs;%WINPYDIR%\Scripts;%PATH%;"
    set "PYTHON=%WINPYDIR%\python.exe "
    set "PIPPATH=%~dp0\python\python-3.9-win\Scripts\pip.exe "
    set "USER_SITE=%~dp0\python\python-3.9-win\site-packages "
)ELSE (
    echo 未检测到内置集成环境，使用系统Python解释器
    set "PYTHON=python.exe "
)

set "REQUIREMENTS_FILE=..\requirements-win-cpu.txt"

SET "TORCH_GPU_FILE=%~dp0pip_packages\torch-2.0.1+cu117-cp39-cp39-win_amd64.whl"
echo %TORCH_GPU_FILE%
if exist %TORCH_GPU_FILE% (
   set "REQUIREMENTS_FILE=..\requirements-win-gpu.txt"
) else (
    echo %TORCH_GPU_FILE% is not exist!
)
echo %REQUIREMENTS_FILE%

rem echo %USER_SITE%
%PIPPATH% install --no-index --find-links=./pip_packages -r %REQUIREMENTS_FILE%

%PYTHON% ../api.py


:end