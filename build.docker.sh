#!/usr/bin/env bash
set -e


python.exe -V

/c/Python312/python.exe -m pip install --upgrade pip
/c/Python312/python.exe -m pip install -r ./app/requirements.txt
/c/Python312/python.exe -m pip install ./sources/Nuitka-2.6.5.tar.gz
/c/Python312/python.exe -m pip install ./sources/undetected-chromedriver-3.5.5-fix-looseversion.tar.gz

icacls ./build.nuitka.sh /grant Everyone:F

./build.nuitka.sh