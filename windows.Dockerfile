# Dockerfile.windows
FROM ghcr.io/nelu/herominer:builder-base
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"
ENV PYTHONUNBUFFERED=1

WORKDIR /build
COPY ./ /build

SHELL ["C:\\git\\bin\\bash.exe", "-c"]

#RUN "Set-ExecutionPolicy Bypass -Scope Process -Force; \
#    & 'C:\\git\\bin\\bash.exe' 'c:\\build\\build.docker.sh'"
# Use PowerShell as the default shell


RUN ls -la /c/

RUN "ls -la /c/build"


RUN "echo $SHELL && pwd && ls -la && printenv"

SHELL ["C:\\git\\bin\\bash.exe", "/c/build/scripts/wsh.sh"]

RUN ls -la /c/

RUN echo $SHELL && pwd && ls -la && printenv

RUN ./build.docker.sh

# Use bash shell as the default entrypoint
ENTRYPOINT ["C:\\git\\git-bash.exe"]
