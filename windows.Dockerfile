# Dockerfile.windows
FROM ghcr.io/nelu/herominer:builder-base
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"
ENV PYTHONUNBUFFERED=1
ENV PATH="C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Tools\\MSVC\\14.39.33519\\bin\\Hostx64\\x64;C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.22621.0\\x64;%PATH%"

WORKDIR /build
COPY ./ /build

RUN python.exe -m pip install -r ./app/requirements.txt \
    && python.exe -m pip install ./sources/Nuitka-2.6.5.tar.gz \
    && python.exe -m pip install ./sources/undetected-chromedriver-3.5.5-fix-looseversion.tar.gz \
    && cmd.exe /c 'icacls c:\build\build.nuitka.sh /grant Everyone:F' \
    &&  ./build.nuitka.sh


# Use bash shell as the default entrypoint
ENTRYPOINT ["C:\\git\\git-bash.exe"]
