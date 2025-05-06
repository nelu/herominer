# Dockerfile.windows
FROM ghcr.io/nelu/herominer:builder-base
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"
ENV PATH="C:\\Program Files\\OpenSSL-Win64\\bin;\
C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Tools\\MSVC\\14.39.33519\\bin\\Hostx64\\x64;\
C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.22621.0\\x64;\
C:\\Python312;\
C:\\Python312\\Scripts;\
C:\\git\\usr\\bin;\
C:\\git\\bin;\
%PATH%"
ENV PYTHONUNBUFFERED=1

# Use PowerShell as the default shell
SHELL ["powershell", "-Command"]

WORKDIR /build
COPY ./ /build

RUN Get-ChildItem -Path . -Recurse

RUN Set-Location -Path 'C:\\build'; Get-ChildItem -Path .; python -v

RUN "python.exe -m pip install --upgrade pip; \
     python.exe -m pip install -r .\\app\\requirements.txt; \
     python.exe -m pip install .\\sources\\Nuitka-2.6.5.tar.gz; \
     python.exe -m pip install .\\sources\\undetected-chromedriver-3.5.5-fix-looseversion.tar.gz; \
     icacls .\\build.nuitka.sh /grant Everyone:F; \
     bash.exe ./build.nuitka.sh"

ENTRYPOINT ["bash.exe"]






