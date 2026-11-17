<#
.SYNOPSIS
    Builds the HeroMiner Windows executables in a resource-sized container.

.DESCRIPTION
    Detects the Windows container host build and selects a base image that can
    actually run on it:
      * host build < 20348 (Windows 10 / Server 2019) -> amitie10g/visualstudio2022-workload-vctools:ltsc2019
      * otherwise                                      -> amitie10g/visualstudio2022-workload-vctools:ltsc2022

    The base image caches the Windows toolchain. The application image caches
    Python dependencies and the current source tree. Nuitka runs in a container
    created from the application image so its Hyper-V CPU and memory resources
    can be configured explicitly.

.PARAMETER BaseImage
    Base image tag to build/use. Defaults to herominer:builder-py313-<osSuffix>.

.PARAMETER AppImage
    Dependency/source image tag to build. Defaults to herominer:app-<osSuffix>.

.PARAMETER AppVersion
    Version passed to the Nuitka build. Defaults to 1.0.0.

.PARAMETER CertPass
    Password for the self-signed certificate. Defaults to $env:CERT_PASS, then
    to MyStrongPassword.

.PARAMETER BuildToolsImage
    Overrides the auto-detected Visual Studio Build Tools base image.

.PARAMETER Isolation
    Optional Docker isolation override (hyperv or process). By default the
    daemon default is used: Hyper-V on Windows clients, process on Windows Server.

.PARAMETER CpuCount
    Number of CPUs assigned to the Nuitka container. Defaults to all logical
    processors reported by the host.

.PARAMETER Memory
    Memory assigned to Docker build steps and the Nuitka container. Defaults to
    half of the host's physical memory.

.PARAMETER CacheVolume
    Docker volume used for persistent Nuitka compiler caches. Defaults to a
    host-OS-specific volume name.

.PARAMETER TryPullBase
    Pull BaseImage first and skip the base build when the pull succeeds.

.PARAMETER PushBase
    Push BaseImage after it has been built (never pushed when pulled/skipped).

.PARAMETER UseBuildKit
    Use BuildKit instead of the classic builder. BuildKit is off by default
    because it cannot execute Windows RUN steps on many engines ("buildkit
    executor not implemented for windows").

.PARAMETER NoCache
    Disable the Docker build cache.

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-docker.ps1 -AppVersion 1.0.0

.EXAMPLE
    .\scripts\build-docker.ps1 -BaseImage ghcr.io/owner/herominer:builder-py313 `
        -AppImage herominer:build-1 -AppVersion 1.0.0 -TryPullBase -PushBase

.NOTES
    The first base image build downloads Visual Studio Build Tools and can take
    30-60 minutes. The Nuitka application build typically takes 10-20 minutes,
    but CI runner resources vary, so do not impose a fixed timeout on it.
#>
[CmdletBinding()]
param(
    [string]$BaseImage,
    [string]$AppImage,
    [string]$AppVersion = '1.0.0',
    [string]$CertPass = $env:CERT_PASS,
    [string]$BuildToolsImage,
    [string]$Isolation,
    [int]$CpuCount,
    [string]$Memory,
    [string]$CacheVolume,
    [switch]$TryPullBase,
    [switch]$PushBase,
    [switch]$UseBuildKit,
    [switch]$NoCache
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Invoke-Docker {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    Write-Host ("> docker " + ($Arguments -join ' '))
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & docker @Arguments 2>&1 | ForEach-Object {
            if ($_ -is [System.Management.Automation.ErrorRecord]) {
                $message = $_.Exception.Message
                if ($message) { Write-Output $message }
            }
            elseif ($_ -is [System.Management.Automation.RemoteException]) {
                if ($_.Message) { Write-Output $_.Message }
            }
            else {
                Write-Output $_
            }
        }
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previous
    }
    if ($exitCode -ne 0) {
        throw "docker $($Arguments[0]) failed with exit code $exitCode"
    }
}

function Invoke-DockerCapture {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $output = & docker @Arguments 2>$null
        return [pscustomobject]@{
            Output   = $output
            ExitCode = $LASTEXITCODE
        }
    }
    finally {
        $ErrorActionPreference = $previous
    }
}

if ($env:OS -ne 'Windows_NT') {
    throw 'This script only supports Windows container builds.'
}

$info = Invoke-DockerCapture -Arguments @('info', '--format', '{{.OSType}}')
if ($info.ExitCode -ne 0) {
    throw 'Unable to query Docker. Is the Docker daemon running?'
}
$serverOs = "$($info.Output)".Trim()
if ($serverOs -ne 'windows') {
    throw "Docker is running in '$serverOs' containers mode. Switch Docker Desktop to Windows containers and retry."
}

$hostBuild = [Environment]::OSVersion.Version.Build
if ($hostBuild -lt 17763) {
    throw "Unsupported Windows host build $hostBuild. Windows 10 1809 or newer is required."
}

if ($hostBuild -lt 20348) {
    $osSuffix = '1809'
    $detectedBuildToolsImage = 'amitie10g/visualstudio2022-workload-vctools:ltsc2019'
}
else {
    $osSuffix = 'ltsc2022'
    $detectedBuildToolsImage = 'amitie10g/visualstudio2022-workload-vctools:ltsc2022'
}

if (-not $BuildToolsImage) {
    $BuildToolsImage = $detectedBuildToolsImage
}
if (-not $BaseImage) {
    $BaseImage = "herominer:builder-py313-$osSuffix"
}
if (-not $AppImage) {
    $AppImage = "herominer:app-$osSuffix"
}
if (-not $CertPass) {
    $CertPass = 'MyStrongPassword'
}

$hostComputer = Get-CimInstance Win32_ComputerSystem
if ($CpuCount -le 0) {
    $CpuCount = [int]$hostComputer.NumberOfLogicalProcessors
}
if (-not $Memory) {
    $memoryGiB = [math]::Max(2, [math]::Floor(($hostComputer.TotalPhysicalMemory / 1GB) / 2))
    $Memory = "${memoryGiB}g"
}
if (-not $CacheVolume) {
    $CacheVolume = "herominer-nuitka-cache-$osSuffix"
}

# BuildKit cannot execute Windows RUN steps on most engines
# ("buildkit executor not implemented for windows"), so the classic builder is
# the default. BuildKit remains available via -UseBuildKit.
$useBuildKit = $false
if ($UseBuildKit) {
    $buildx = Invoke-DockerCapture -Arguments @('buildx', 'version')
    if ($buildx.ExitCode -ne 0) {
        throw 'BuildKit requested but the buildx plugin is not available.'
    }
    $useBuildKit = $true
    $env:DOCKER_BUILDKIT = '1'
}
else {
    $env:DOCKER_BUILDKIT = '0'
}

$commonArgs = @('build', '--memory', $Memory)
if ($useBuildKit) {
    $commonArgs += '--progress=plain'
}
if ($Isolation) {
    if ($useBuildKit) {
        Write-Warning "BuildKit ignores --isolation; relying on the daemon default isolation instead."
    }
    else {
        $commonArgs += @('--isolation', $Isolation)
    }
}
if ($NoCache) {
    $commonArgs += '--no-cache'
}

Write-Host "Host build   : $hostBuild"
Write-Host "Base image   : $BaseImage"
Write-Host "Tools image  : $BuildToolsImage"
Write-Host "App image    : $AppImage"
Write-Host "App version  : $AppVersion"
Write-Host "Builder      : $(if ($useBuildKit) { 'BuildKit' } else { 'classic' })"
Write-Host "Nuitka CPUs  : $CpuCount"
Write-Host "Nuitka memory: $Memory"
Write-Host "Nuitka cache : $CacheVolume"

$skipBaseBuild = $false
if ($TryPullBase) {
    Write-Host "Trying to pull base image $BaseImage..."
    $pulled = $false
    try {
        Invoke-Docker -Arguments @('pull', $BaseImage)
        $pulled = $true
    }
    catch {
        Write-Host 'Base image not available; it will be built.'
    }
    if ($pulled) {
        Write-Host 'Base image pulled; skipping base build.'
        $skipBaseBuild = $true
    }
}

if (-not $skipBaseBuild) {
    $baseArgs = $commonArgs + @(
        '-f', 'base.Dockerfile',
        '--build-arg', "BUILD_TOOLS_IMAGE=$BuildToolsImage",
        '-t', $BaseImage,
        '.'
    )

    $baseStart = Get-Date
    Invoke-Docker -Arguments $baseArgs
    $baseElapsed = (Get-Date) - $baseStart
    Write-Host ("Base image built in {0:n1} min." -f $baseElapsed.TotalMinutes)

    if ($PushBase) {
        Invoke-Docker -Arguments @('push', $BaseImage)
    }
}

$appArgs = $commonArgs + @(
    '-f', 'windows.Dockerfile',
    '--build-arg', "BASE_IMAGE=$BaseImage",
    '-t', $AppImage,
    '.'
)

$appStart = Get-Date
Invoke-Docker -Arguments $appArgs
$appElapsed = (Get-Date) - $appStart
Write-Host ("Dependency/source image built in {0:n1} min." -f $appElapsed.TotalMinutes)

$env:APP_VERSION = $AppVersion
$env:CERT_PASS = $CertPass
$containerName = "herominer-build-$([guid]::NewGuid().ToString('N').Substring(0, 12))"
$runArgs = @(
    'run',
    '--name', $containerName,
    '--cpu-count', "$CpuCount",
    '--memory', $Memory,
    '--env', 'APP_VERSION',
    '--env', 'CERT_PASS',
    '--env', 'NUITKA_CACHE_DIR=C:\nuitka-cache',
    '--mount', "type=volume,source=$CacheVolume,target=C:\nuitka-cache"
)
if ($Isolation) {
    $runArgs += @('--isolation', $Isolation)
}
$runArgs += @($AppImage, './build.nuitka.sh')

$buildStart = Get-Date
try {
    Invoke-Docker -Arguments $runArgs

    $releaseDir = Join-Path $repoRoot 'release'
    New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null
    foreach ($artifact in @('cli.exe', 'input.exe', 'run.cmd')) {
        $destination = Join-Path $releaseDir $artifact
        Invoke-Docker -Arguments @('cp', "${containerName}:/build/release/$artifact", $destination)
    }

    $cliPath = Join-Path $releaseDir 'cli.exe'
    $cliFileVersion = (Get-Item -LiteralPath $cliPath).VersionInfo.FileVersion
    if ($cliFileVersion -ne $AppVersion -and -not $cliFileVersion.StartsWith("$AppVersion.")) {
        throw "cli.exe version '$cliFileVersion' does not match requested version '$AppVersion'."
    }

    foreach ($artifact in @('cli.exe', 'input.exe')) {
        $artifactPath = Join-Path $releaseDir $artifact
        $signature = Get-AuthenticodeSignature -LiteralPath $artifactPath
        if ($signature.SignatureType -ne 'Authenticode' -or -not $signature.SignerCertificate) {
            throw "$artifact does not contain an Authenticode signature."
        }
        Write-Host "$artifact signature: $($signature.Status) ($($signature.SignerCertificate.Subject))"
    }

    $runCommand = Get-Content -LiteralPath (Join-Path $releaseDir 'run.cmd') -Raw
    foreach ($reference in @('input.exe', 'cli.exe')) {
        if ($runCommand -notmatch [regex]::Escape($reference)) {
            throw "run.cmd does not reference $reference."
        }
    }

    $releaseMount = "type=bind,source=$releaseDir,target=C:\artifacts,readonly"
    Invoke-Docker -Arguments @(
        'run', '--rm',
        '--cpu-count', '2',
        '--memory', '4g',
        '--env', 'HM_DISABLE_REDIS_LOGGING=1',
        '--mount', $releaseMount,
        $AppImage, './scripts/test-release.sh', '/c/artifacts'
    )

    Get-FileHash -Algorithm SHA256 -LiteralPath (
        @('cli.exe', 'input.exe', 'run.cmd') | ForEach-Object { Join-Path $releaseDir $_ }
    ) | ForEach-Object { Write-Host "$($_.Path): $($_.Hash)" }
}
catch {
    $container = Invoke-DockerCapture -Arguments @('container', 'inspect', '--format', '{{.Id}}', $containerName)
    if ($container.ExitCode -eq 0) {
        Write-Warning "Build container '$containerName' was retained for inspection."
        Write-Host "  docker logs $containerName"
        Write-Host "  docker inspect $containerName"
        Write-Host "  docker diff $containerName"
        Write-Host "  docker rm $containerName"
    }
    throw
}

$buildElapsed = (Get-Date) - $buildStart
Invoke-Docker -Arguments @('rm', $containerName)

Write-Host ("Nuitka artifacts built and extracted in {0:n1} min." -f $buildElapsed.TotalMinutes)
Write-Host ''
Write-Host 'Done:'
Write-Host "  base image : $BaseImage"
Write-Host "  build image: $AppImage"
Write-Host "  artifacts  : $(Join-Path $repoRoot 'release')"
