<#
.SYNOPSIS
    Builds the HeroMiner Windows container images using a host-compatible base image.

.DESCRIPTION
    Detects the Windows container host build and selects a base image that can
    actually run on it:
      * host build < 20348 (Windows 10 / Server 2019) -> mcr.microsoft.com/windows-cssc/python:3.13-servercore-ltsc2019
      * otherwise                                      -> mcr.microsoft.com/windows-cssc/python:3.13-servercore-ltsc2022

    The base image tag defaults to a host-specific suffix so a local Windows 10
    build can never overwrite the CI base image in GHCR.

.PARAMETER BaseImage
    Base image tag to build/use. Defaults to herominer:builder-py313-<osSuffix>.

.PARAMETER AppImage
    Application image tag to build. Defaults to herominer:app-<osSuffix>.

.PARAMETER AppVersion
    Version passed to the Nuitka build. Defaults to 1.0.0.

.PARAMETER CertPass
    Password for the self-signed certificate. Defaults to $env:CERT_PASS, then
    to MyStrongPassword.

.PARAMETER PythonImage
    Overrides the auto-detected Python base image.

.PARAMETER Isolation
    Optional Docker isolation override (hyperv or process). By default the
    daemon default is used: Hyper-V on Windows 10, process on Windows Server.

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
    [string]$PythonImage,
    [string]$Isolation,
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
    $detectedPythonImage = 'mcr.microsoft.com/windows-cssc/python:3.13-servercore-ltsc2019'
}
else {
    $osSuffix = 'ltsc2022'
    $detectedPythonImage = 'mcr.microsoft.com/windows-cssc/python:3.13-servercore-ltsc2022'
}

if (-not $PythonImage) {
    $PythonImage = $detectedPythonImage
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

$commonArgs = @('build')
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
Write-Host "Python image : $PythonImage"
Write-Host "App image    : $AppImage"
Write-Host "App version  : $AppVersion"
Write-Host "Builder      : $(if ($useBuildKit) { 'BuildKit' } else { 'classic' })"

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
        '--build-arg', "PYTHON_IMAGE=$PythonImage",
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

$env:CERT_PASS = $CertPass
$appArgs = $commonArgs + @(
    '-f', 'windows.Dockerfile',
    '--build-arg', "BASE_IMAGE=$BaseImage",
    '--build-arg', "APP_VERSION=$AppVersion",
    '--build-arg', 'CERT_PASS',
    '-t', $AppImage,
    '.'
)

$appStart = Get-Date
Invoke-Docker -Arguments $appArgs
$appElapsed = (Get-Date) - $appStart
Write-Host ("Application image built in {0:n1} min." -f $appElapsed.TotalMinutes)

Write-Host ''
Write-Host 'Done. Images:'
Write-Host "  base: $BaseImage"
Write-Host "  app : $AppImage"
Write-Host ''
Write-Host 'Extract artifacts with:'
Write-Host "  `$c = docker create $AppImage"
Write-Host '  docker cp "${c}:/build/release/cli.exe" .\release\'
Write-Host '  docker cp "${c}:/build/release/input.exe" .\release\'
Write-Host '  docker cp "${c}:/build/release/run.cmd" .\release\'
Write-Host '  docker rm $c'
