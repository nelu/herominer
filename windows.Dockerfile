# Dockerfile.windows
FROM ghcr.io/nelu/herominer:builder-base
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"
WORKDIR /build
COPY . .


# RUN ["cmd", "/C", "dir", "C:\\git\\usr\\bin\\"]

# Switch to BusyBox sh shell
SHELL ["C:\\busybox.exe", "sh", "-c"]

RUN ls -la ./
RUN which python.exe

RUN "python.exe -m pip install --upgrade pip; \
     python.exe -m pip install -r app\\requirements.txt; \
     python.exe -m pip install C:\\build\\sources\\Nuitka-2.6.5.tar.gz; \
     python.exe -m pip install C:\\build\\sources\\undetected-chromedriver-3.5.5-fix-looseversion.tar.gz"

RUN chmod +x ./build.nuitka.sh && ./build.nuitka.sh

# Optional: return shell to cmd or powershell
#SHELL ["powershell", "-Command"]






