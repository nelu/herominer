# Dockerfile.windows
FROM ghcr.io/nelu/herominer:builder-base
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"
ENV PYTHONUNBUFFERED=1

WORKDIR /build
COPY ./ /build

# Use PowerShell as the default shell
SHELL ["powershell", "-Command"]

RUN Get-ChildItem -Path 'C:\'

RUN Get-ChildItem -Path C:\build

RUN Get-ChildItem -Path C:\git

#RUN "Set-ExecutionPolicy Bypass -Scope Process -Force; \
#    & 'C:\\git\\bin\\bash.exe' 'c:\\build\\build.docker.sh'"
# Use PowerShell as the default shell
SHELL ["C:\\git\\bin\\bash.exe", "-c"]

RUN ls /c/
# Use bash shell as the default entrypoint
ENTRYPOINT ["C:\\git\\bin\\bash.exe"]
