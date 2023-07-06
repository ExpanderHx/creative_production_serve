CURDIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd )
echo $CURDIR

WINPYDIR=${CURDIR}\python\python-3.9-win
echo $WINPYDIR

if [ -d ${WINPYDIR} ];then
  echo "检测到内置集成环境，使用内置Python解释器"
  PATH=${WINPYDIR}\;${WINPYDIR}\DLLs;${WINPYDIR}\Scripts;${PATH};
  PYTHON=${WINPYDIR}\python.exe
  PIPPATH=${WINPYDIR}\Scripts\pip.exe
  USER_SITE=${WINPYDIR}\site-packages
  echo $PATH
else
  echo "未检测到内置集成环境，使用系统Python解释器"
  set PYTHON=python
fi


REQUIREMENTS_FILE="..\requirements-max-cpu.txt"

$PIPPATH install --no-index --find-links=./pip_packages -r $REQUIREMENTS_FILE

$PYTHON ../api.py