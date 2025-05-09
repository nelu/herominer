# Dockerfile.windows
FROM ghcr.io/nelu/herominer:builder-base
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"
ENV PYTHONUNBUFFERED=1

# Use PowerShell as the default shell
SHELL ["powershell", "-Command"]

WORKDIR /build
COPY ./ /build

RUN "& 'C:\\Python312\\python.exe' '-V'"

RUN "& 'C:\\Python312\\python.exe' -m pip install --upgrade pip; \
     & 'C:\\Python312\\python.exe' -m pip install -r '.\\app\\requirements.txt'; \
     & 'C:\\Python312\\python.exe' -m pip install '.\\sources\\Nuitka-2.6.5.tar.gz'; \
     & 'C:\\Python312\\python.exe' -m pip install '.\\sources\\undetected-chromedriver-3.5.5-fix-looseversion.tar.gz'; \
     icacls '.\\build.nuitka.sh' /grant Everyone:F; \
     & 'C:\\git\\bin\\bash.exe' './build.nuitka.sh'"

ENTRYPOINT ["C:\\git\\bin\\bash.exe"]
