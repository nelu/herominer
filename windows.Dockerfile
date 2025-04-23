# Dockerfile.windows
FROM ghcr.io/nelu/herominer:builder-base
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"

ENV PYTHONUNBUFFERED=1
# Now set Git Bash as the shell
SHELL ["bash.exe", "-c"]


WORKDIR /build
COPY ./ /build

RUN ls -la ./

RUN cd /c/build && ls -la ./ && python -v

RUN sh -c "python.exe -m pip install --upgrade pip && \
    python.exe -m pip install -r ./app/requirements.txt && \
    python.exe -m pip install ./sources/Nuitka-2.6.5.tar.gz && \
    python.exe -m pip install ./sources/undetected-chromedriver-3.5.5-fix-looseversion.tar.gz \
    && chmod 775 ./build.nuitka.sh \
    && ./build.nuitka.sh "

ENTRYPOINT ["bash.exe"]






