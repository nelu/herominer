# Building the Windows executables

`scripts/build-docker.ps1` prepares two Docker images, runs Nuitka in a
resource-sized container, and copies the release files to `release/`. It detects
the container host OS and picks a base image that can actually run on it:

| Host | Base image | Isolation |
| --- | --- | --- |
| Windows 10 / Server 2019 (build < 20348) | `amitie10g/visualstudio2022-workload-vctools:ltsc2019` | Hyper-V (Docker Desktop default) |
| Windows 11 / Server 2022+ (build >= 20348) | `amitie10g/visualstudio2022-workload-vctools:ltsc2022` | Hyper-V on Windows clients; process on Server |

Windows 10 cannot run `ltsc2022` images, even with Hyper-V isolation. This is why
the base image is selected per host instead of being hardcoded.

## Prerequisites

- Docker Desktop running in **Windows containers** mode (`docker info` must
  report `OSType: windows`).
- Windows 10 1809+ or Windows Server 2019+.
- Enough disk space for Visual Studio Build Tools (tens of GB).

## Build stages

- The base image caches Visual Studio Build Tools, Python, Git, and supporting
  tools that are expensive to install.
- The application image caches the current Python dependencies and source tree.
- A temporary container runs `build.nuitka.sh` with an explicit CPU count and
  memory allocation. This avoids the two-vCPU and 1 GiB defaults of a Hyper-V
  isolated container.
- The script copies `cli.exe`, `input.exe`, and `run.cmd` to `release/`, validates
  them locally in a disposable container, then removes the successful build
  container.

Python dependencies are copied and installed before the rest of the source, so
normal source changes do not invalidate the dependency layer.

## Local build

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-docker.ps1 -AppVersion 1.0.0
```

This produces:

- `herominer:builder-py313-1809` (base image)
- `herominer:app-1809` (dependency/source image)
- `release/cli.exe`
- `release/input.exe`
- `release/run.cmd`

On Windows 11/Server 2022+ the default tags end in `-ltsc2022` instead.

The local build validates the `cli.exe` version, confirms that both executables
contain Authenticode signatures, tests the `input.exe` SFX archive, and runs
`--help` against both executable payloads in a disposable container. Redis
logging is disabled only inside that smoke-test container. The build also prints
SHA-256 hashes for the extracted artifacts.

By default, the Nuitka container receives all host logical processors and half
of the host's physical memory. Override these values when the host must retain
more resources:

```powershell
.\scripts\build-docker.ps1 -CpuCount 12 -Memory 16g
```

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

## Inspect the build image

The application image opens Bash by default and does not automatically start a
Nuitka build:

```powershell
docker run --rm -it herominer:app-1809
```

If the Nuitka build or artifact extraction fails, the script retains the
stopped build container and prints its name. Use `docker logs`, `docker inspect`,
`docker diff`, or `docker cp` to investigate it, then remove it manually.

## Timeouts

These builds are slow, and CI runner resources vary. Do not impose a fixed
timeout on the Nuitka application build:

- First base image build (Visual Studio Build Tools download/install):
  typically 30-60 minutes.
- Nuitka application build: typically 10-20 minutes, but may take longer
  depending on the runner.

## Measured Nuitka cache result

On a 24-logical-CPU Windows 10 host with 31 GiB assigned to the container, the
first cold Nuitka build took 26 minutes 48 seconds. Repeating the same build with
the `herominer-nuitka-cache-1809` volume took 15 minutes 12 seconds, a 43.3%
reduction.

| Target | Cold build | Warm build | Warm cache result |
| --- | ---: | ---: | --- |
| `input.exe` | 7m 37s | 5m 42s | 249 hits, 0 misses |
| `cli.exe` | 19m 11s | 9m 07s | 1,194 hits, 0 misses |
| Total Nuitka stage | 26m 48s | 15m 12s | 1,443 hits, 0 misses |

The generated onefile bootstrap is a separate single-file compilation and had
one miss. After changing one Python module, the next build retained 248/249 hits
for `input.exe` and 1,193/1,194 hits for `cli.exe`, confirming that unchanged
translation units remain cached.

## Useful options

- `-NoCache` - rebuild without the Docker layer cache.
- `-BuildToolsImage <image>` - override the auto-detected Visual Studio Build
  Tools base image.
- `-CpuCount <count>` - CPUs assigned to the Nuitka container. Defaults to all
  host logical processors.
- `-Memory <size>` - memory assigned to image build steps and the Nuitka
  container. Defaults to half of host RAM.
- `-CacheVolume <name>` - persistent Docker volume for Nuitka and compiler
  caches. Defaults to `herominer-nuitka-cache-<osSuffix>`.
- `-Isolation hyperv|process` - override isolation. BuildKit ignores this for
  image builds, but it is still applied to the Nuitka container.
- `-CertPass <password>` - certificate password. Defaults to `$env:CERT_PASS`,
  then `MyStrongPassword`.
