# Dockerfile.base
FROM python:3.12.6-windowsservercore-ltsc2022
LABEL org.opencontainers.image.source="https://github.com/nelu/herominer"
COPY ./scripts/wsh.sh /wsh.sh
COPY ./sources /build/sources

SHELL ["powershell", "-Command"]
--add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK.22621
# Install Chocolatey and all packages in a single session
RUN "Set-ExecutionPolicy Bypass -Scope Process -Force; \
     Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1')); \
     choco install visualstudio2022buildtools --params '--add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK.22621' -y; \
     choco install 7zip.install -y; \
     choco install openssl.light -y; \
     Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.1/PortableGit-2.42.0-64-bit.7z.exe' -OutFile 'git.7z.exe'; \
     & 'C:\\Program Files\\7-Zip\\7z.exe' x git.7z.exe -oC:\\git -y; \
     Remove-Item 'git.7z.exe'"

SHELL ["C:\\git\\bin\\bash.exe", "c:\\wsh.sh"]

RUN python.exe -m pip install -r /c/build/sources/requirements.txt \
    && python.exe -m pip install /c/build/sources/Nuitka-2.6.5.tar.gz \
    && python.exe -m pip install /c/build/sources/undetected-chromedriver-3.5.5-fix-looseversion.tar.gz

## Set path (replace MSVC version as needed)
#ENV PATH="C:\\Program Files\\OpenSSL-Win64\\bin;\
#C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Tools\\MSVC\\14.39.33519\\bin\\Hostx64\\x64;\
#C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.22621.0\\x64;\
#C:\\git\\usr\\bin;\
#C:\\git\\bin;\
#${PATH}"

ENV SEVEN_ZIP="/c/Program Files/7-Zip/7z.exe"
