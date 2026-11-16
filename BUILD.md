# Building the Windows container images

`scripts/build-docker.ps1` builds the Docker base image and the Nuitka
application image. It detects the container host OS and picks a base image that
can actually run on it:

| Host | Base image | Isolation |
| --- | --- | --- |
| Windows 10 / Server 2019 (build < 20348) | `mcr.microsoft.com/windows-cssc/python:3.13-servercore-ltsc2019` | Hyper-V (Docker Desktop default) |
| Windows 11 / Server 2022+ (build >= 20348) | `mcr.microsoft.com/windows-cssc/python:3.13-servercore-ltsc2022` | process (daemon default) |

Windows 10 cannot run `ltsc2022` images, even with Hyper-V isolation. This is why
the base image is selected per host instead of being hardcoded.

## Prerequisites

- Docker Desktop running in **Windows containers** mode (`docker info` must
  report `OSType: windows`).
- Windows 10 1809+ or Windows Server 2019+.
- Enough disk space for Visual Studio Build Tools (tens of GB).

## Local build (Windows 10)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-docker.ps1 -AppVersion 1.0.0
```

This produces:

- `herominer:builder-py313-1809` (base image)
- `herominer:app-1809` (application image)

On Windows 11/Server 2022+ the default tags end in `-ltsc2022` instead.

## CI-equivalent build

```powershell
.\scripts\build-docker.ps1 `
  -BaseImage ghcr.io/owner/herominer:builder-py313 `
  -AppImage herominer:build-1 `
  -AppVersion 1.0.0 `
  -TryPullBase -PushBase
```

`-TryPullBase` pulls an existing base image and skips rebuilding it.
`-PushBase` only pushes when the base image was actually built.

## Extract the release files

```powershell
$c = docker create herominer:app-1809
docker cp "${c}:/build/release/cli.exe" .\release\
docker cp "${c}:/build/release/input.exe" .\release\
docker cp "${c}:/build/release/run.cmd" .\release\
docker rm $c
```

## Timeouts

These builds are slow, and CI runner resources vary. Do not impose a fixed
timeout on the Nuitka application build:

- First base image build (Visual Studio Build Tools download/install):
  typically 30-60 minutes.
- Nuitka application build: typically 10-20 minutes, but may take longer
  depending on the runner.

## Useful options

- `-NoCache` - rebuild without the Docker layer cache.
- `-PythonImage <image>` - override the auto-detected Python base image.
- `-Isolation hyperv|process` - override isolation (classic builder only; the
  daemon default is used with BuildKit).
- `-CertPass <password>` - certificate password. Defaults to `$env:CERT_PASS`,
  then `MyStrongPassword`.
