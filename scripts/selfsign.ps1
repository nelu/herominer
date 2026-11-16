#!/usr/bin/env powershell
# Define parameters
param(
    [string]$certPfxPath,
    [string]$pfxPassword,
    [string]$exeToSign
)

$ErrorActionPreference = "Stop"

if (-not $certPfxPath)
{
    $certPfxPath = ".\config\myapp.pfx"
}
if (-not $pfxPassword)
{
    $pfxPassword = "MyStrongPassword"
}
if (-not $exeToSign)
{
    $exeToSign = ".\release\cli.exe"
}

# Step 1: Check if certificate exists, and generate if missing
if (-not (Test-Path $certPfxPath))
{
    Write-Host "No certificate found at $certPfxPath. Running generate-cert.sh..."

    $bashScript = "./scripts/generate-cert.sh"
    if (-not (Test-Path $bashScript))
    {
        Write-Error "Cannot find $bashScript. Please ensure it exists and try again."
        exit 1
    }

    & bash $bashScript

    if (-not (Test-Path $certPfxPath))
    {
        Write-Error "Certificate generation failed or file not found after script run."
        exit 1
    }
    # Step 2: Optionally install certificate to Trusted Root
    $runningInDocker = Test-Path "C:\.dockerenv"

    if ($runningInDocker)
    {
        Write-Host "Running inside Docker - skipping Trusted Root installation."
    }
    elseif ($env:ADD_TO_TRUSTED_ROOT -ieq "y")
    {
        $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
        $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath\add-to-trusted-root.ps1`" -certPfxPath `"$certPfxPath`" -pfxPassword `"$pfxPassword`""

        if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))
        {
            Write-Host "Elevating to install certificate into Trusted Root..."
            Start-Process PowerShell -ArgumentList $arguments -Verb RunAs -Wait
        }
        else
        {
            Write-Host "Running Trusted Root installation..."
            & PowerShell -ExecutionPolicy Bypass -File "$scriptPath\add-to-trusted-root.ps1" -certPfxPath "$certPfxPath" -pfxPassword "$pfxPassword"
        }
    }
    else
    {
        Write-Host "Skipping Trusted Root installation (set ADD_TO_TRUSTED_ROOT=y to install)."
    }
}

# Step 3: Sign the executable
if (-not (Test-Path $exeToSign))
{
    Write-Error "Executable to sign not found: $exeToSign"
    exit 1
}

Write-Host "Signing: $exeToSign"
$resolvedCertPath = (Resolve-Path $certPfxPath).Path
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($resolvedCertPath, $pfxPassword, [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::Exportable)
if (-not $cert)
{
    Write-Error "Failed to load certificate from $certPfxPath"
    exit 1
}

$sig = Set-AuthenticodeSignature -FilePath $exeToSign -Certificate $cert -HashAlgorithm SHA256
if ($null -eq $sig)
{
    Write-Error "Failed to sign ${exeToSign}: no signature result"
    exit 1
}

$verify = Get-AuthenticodeSignature -FilePath $exeToSign
Write-Host "Signature status for ${exeToSign}: $($verify.Status)"
if ($verify.StatusMessage) { Write-Host $verify.StatusMessage }
if ($verify.Status -eq "NotSigned" -or $verify.Status -eq "HashMismatch")
{
    Write-Error "Executable signing failed: $exeToSign ($($verify.Status))"
    exit 1
}
