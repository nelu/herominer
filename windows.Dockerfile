# Dockerfile.windows
FROM ghcr.io/nelu/herominer:builder-base
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"
ENV PYTHONUNBUFFERED=1

WORKDIR /build
COPY ./ /build

RUN python.exe -m pip install -r ./app/requirements.txt \
    && python.exe -m pip install ./sources/Nuitka-2.6.5.tar.gz \
    && python.exe -m pip install ./sources/undetected-chromedriver-3.5.5-fix-looseversion.tar.gz \
    && cmd.exe /c 'icacls c:\build\build.nuitka.sh /grant Everyone:F' \
    &&  ./build.nuitka.sh


# Use bash shell as the default entrypoint
ENTRYPOINT ["C:\\git\\git-bash.exe"]
