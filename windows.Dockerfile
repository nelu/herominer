# Dockerfile.windows
FROM ghcr.io/nelu/herominer:builder-base
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"
WORKDIR /build
COPY . .

# Now set Git Bash as the shell
SHELL ["C:\\git\\usr\\bin\\bash.exe", "-c"]

RUN python.exe -m pip install --upgrade pip && \
    python.exe -m pip install -r ./app/requirements.txt && \
    python.exe -m pip install ./sources/Nuitka-2.6.5.tar.gz && \
    python.exe -m pip install ./sources/undetected-chromedriver-3.5.5-fix-looseversion.tar.gz \
    && cd ./build && chmod 775 ./build.nuitka.sh \
    && ./build.nuitka.sh

CMD ["bash.exe"]





