# Dockerfile.windows
ARG BASE_IMAGE=ghcr.io/nelu/herominer:builder-py311
FROM ${BASE_IMAGE}
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"

ARG APP_VERSION=1.0.0
ARG CERT_PASS

RUN rm -rf /c/build/app /c/build/src

WORKDIR /build
COPY ./ /build

# update dependencies
RUN python.exe -m pip install -r /c/build/requirements.lock \
    && python.exe -m pip install /c/build/sources/Nuitka-2.6.5.tar.gz \
    && python.exe -m pip install /c/build/sources/undetected-chromedriver-3.5.5-fix-looseversion.tar.gz \
    && python.exe -m pip install --no-deps --no-build-isolation /c/build \
    && cmd.exe /c 'icacls c:\build\build.nuitka.sh /grant Everyone:F' \
    &&  ./build.nuitka.sh


# Use bash shell as the default entrypoint
ENTRYPOINT ["C:\\git\\git-bash.exe"]
