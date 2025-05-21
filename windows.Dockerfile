# Dockerfile.windows
FROM ghcr.io/nelu/herominer:builder-base
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"

RUN rm -rf /c/build/app

WORKDIR /build
COPY ./ /build

# update dependencies
RUN python.exe -m pip install -r /c/build/sources/requirements.txt \
    && python.exe -m pip install /c/build/sources/Nuitka-2.6.5.tar.gz \
    && python.exe -m pip install /c/build/sources/undetected-chromedriver-3.5.5-fix-looseversion.tar.gz \
    && cmd.exe /c 'icacls c:\build\build.nuitka.sh /grant Everyone:F' \
    &&  ./build.nuitka.sh


# Use bash shell as the default entrypoint
ENTRYPOINT ["C:\\git\\git-bash.exe"]
