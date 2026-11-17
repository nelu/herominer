# Dockerfile.windows
ARG BASE_IMAGE=ghcr.io/nelu/herominer:builder-py313
FROM ${BASE_IMAGE}
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"

RUN rm -rf /c/build/app /c/build/src

WORKDIR /build
COPY ./requirements.lock /build/requirements.lock

RUN python.exe -m pip install -r /c/build/requirements.lock \
    && python.exe -m pip install "Nuitka==4.3.5" \
    && python.exe -m pip check

COPY ./ /build

RUN python.exe -m pip install --no-deps --no-build-isolation /c/build \
    && python.exe -m pip check

# Use bash shell as the default entrypoint
ENTRYPOINT ["C:\\Program Files\\Git\\bin\\bash.exe"]
