@echo off
chcp 65001

rem @echo off 关闭之后所有命令的回显，不然bat文件中每条指令会在cmd命令窗口显示
rem 注释，还有::也表示注释
rem @echo off
rem echo 路径1.2：%cd%
rem echo 路径2：%~dp0
cd /d %~dp0
set "WINPYDIR=%~dp0\python\python-3.9.13-win"
echo  %~dp0
IF EXIST %WINPYDIR% (
echo 检测到新版集成环境，使用内置Python解释器
set "PATH=%WINPYDIR%\;%WINPYDIR%\DLLs;%WINPYDIR%\Scripts;%PATH%;"
set "PYTHON=%WINPYDIR%\python.exe "
set "PIPPATH=%~dp0\python\python-3.9.13-win\Scripts\pip.exe "
set "USER_SITE=%~dp0\python\python-3.9.13-win\site-packages "
)
IF EXIST python (
echo 未检测到集成环境，使用系统Python解释器
set "PYTHON=python.exe "
)ELSE (
)

rem echo %USER_SITE%
%PIPPATH% install --no-index --find-links=./pip_packages -r ../requirements.txt

%PYTHON% ../api.py
rem %PYTHON% E:\pycharm\creative_production_serve\api.py

rem %PIPPATH% -V

rem E:\pycharm\creative_production_serve\serve_system\python\python-3.9.13-win\Scripts\pip.exe -V

rem D:\BaiduNetdiskDownload\wenda\wd-git_6.2\wenda\WPy64-31110\python-3.11.1.amd64\Scripts\pip.exe -V
rem D:\ProgramData\anaconda3\envs\creative_production_serve_test\Scripts\pip.exe -V
rem %PYTHON% -m pip -V
rem E:\pycharm\creative_production_serve\serve_system\python\python-3.9.13-win\Scripts\pip.exe -V
rem pip -V

rem %PYTHON% -m pip -v


rem cd /d %~dp0
rem start python/python-3.9.13-win/Scripts/pip.exe install --no-index --find-links=./pip_packages -r requirements.txt
rem start python/python-3.9.13-win/python.exe ../api.py

rem E:\pycharm\creative_production_serve\serve_system\python\python-3.9.13-win\Scripts\pip.exe install --no-index --find-links=./pip_packages -r requirements.txt
rem E:\pycharm\creative_production_serve\serve_system\python\python-3.9.13-win\python.exe ../api.py

:end