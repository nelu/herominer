# Dockerfile.windows
FROM ghcr.io/nelu/herominer:builder-base
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"

ENV PYTHONUNBUFFERED=1

# Use PowerShell as the default shell
SHELL ["powershell", "-Command"]

WORKDIR /build
COPY ./ /build

RUN Get-ChildItem -Path . -Recurse

RUN Set-Location -Path 'C:\\build'; Get-ChildItem -Path .; python -v

RUN python.exe -m pip install --upgrade pip; `
    python.exe -m pip install -r .\\app\\requirements.txt; `
    python.exe -m pip install .\\sources\\Nuitka-2.6.5.tar.gz; `
    python.exe -m pip install .\\sources\\undetected-chromedriver-3.5.5-fix-looseversion.tar.gz; `
    icacls .\\build.nuitka.sh /grant Everyone:F; `
    bash.exe ./build.nuitka.sh  # Keep this if build script requires bash

ENTRYPOINT ["bash.exe"]






