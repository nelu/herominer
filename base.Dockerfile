# Dockerfile.base
ARG BUILD_TOOLS_IMAGE=amitie10g/visualstudio2022-workload-vctools:ltsc2022

FROM ${BUILD_TOOLS_IMAGE}
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"

COPY ./scripts/wsh.sh /wsh.sh
COPY ./requirements.lock /build/requirements.lock

SHELL ["powershell", "-Command"]

RUN "choco install python --version=3.13.17 -y; \
     choco install 7zip.install -y; \
     choco install openssl.light -y; \
     choco install git.install --version=2.56.1 --params '/NoShellIntegration /NoAutoCrlf /GitAndUnixToolsOnPath' -y; \
     if (-not (Get-ChildItem 'C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe' -ErrorAction SilentlyContinue)) { throw 'Windows SDK signing tools were not installed' }; \
     if (-not (Test-Path 'C:\Program Files\Git\bin\bash.exe')) { throw 'Git Bash was not installed' }; \
     if (-not (Test-Path 'C:\Program Files\Git\git-bash.exe')) { throw 'Git Bash launcher was not installed' }"

RUN "$vcPath = & 'C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe' -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath; \
     if (-not $vcPath) { throw 'Visual C++ build tools were not installed' }"

RUN "$cs = Get-CimInstance Win32_ComputerSystem; Write-Host 'CPUs:' $cs.NumberOfLogicalProcessors '| RAM (GB):' ([math]::Round($cs.TotalPhysicalMemory / 1GB, 2))"

SHELL ["bash.exe", "c:\\wsh.sh"]

RUN python.exe -m pip install -r /c/build/requirements.lock \
    && python.exe -m pip install "Nuitka==4.3.5" \
    && python.exe -m pip check



ENV SEVEN_ZIP="/c/Program Files/7-Zip/7z.exe"
