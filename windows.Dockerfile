# Dockerfile.windows
FROM ghcr.io/nelu/herominer:builder-base
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"
ENV PYTHONUNBUFFERED=1

WORKDIR /build
COPY ./ /build

SHELL ["C:\\git\\bin\\bash.exe", "./scripts/wsh.sh"]

RUN ls -la /c/

RUN echo $SHELL && pwd && ls -la && printenv

RUN icacls ./build.nuitka.sh /grant Everyone:F \
    && python.exe -m pip install --upgrade pip \
    && python.exe -m pip install -r ./app/requirements.txt \
    && python.exe -m pip install ./sources/Nuitka-2.6.5.tar.gz \
    && python.exe -m pip install ./sources/undetected-chromedriver-3.5.5-fix-looseversion.tar.gz \
    && ./build.nuitka.sh


# Use bash shell as the default entrypoint
ENTRYPOINT ["C:\\git\\git-bash.exe"]
