# Dockerfile.base
FROM mcr.microsoft.com/windows/servercore:ltsc2022
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"

SHELL ["powershell", "-Command"]

# Install some sh
# RUN Invoke-WebRequest -Uri "https://frippery.org/files/busybox/busybox.exe" -OutFile "C:\\busybox.exe"
COPY ./sources/busybox.exe /busybox.exe


# Install Chocolatey and all packages in a single session
RUN "Set-ExecutionPolicy Bypass -Scope Process -Force; \
     Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1')); \
     & choco install python --version=3.12.6 -y; \
     choco install visualstudio2022buildtools --params '--add Microsoft.VisualStudio.Component.VC.Tools.x86.x64' -y; \
     choco install 7zip.install -y; \
     choco install openssl.light -y"

# Set path (replace MSVC version as needed)
ENV PATH="C:\\Program Files\\OpenSSL-Win64\\bin;\
C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Tools\\MSVC\\14.39.33519\\bin\\Hostx64\\x64;\
C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.22621.0\\x64;\
C:\\Python312;\
C:\\Python312\\Scripts;\
C:\\git\\bin;\
%PATH%"

ENV SEVEN_ZIP="/c/Program Files/7-Zip/7z.exe"
