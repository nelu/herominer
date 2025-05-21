#!/usr/bin/env powershell
# Define parameters
param(
    [string]$certPfxPath,
    [string]$pfxPassword,
    [string]$exeToSign
)

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
    else
    {
        $addToTrustedRoot = Read-Host "Do you want to add the certificate to Trusted Root Authorities? (y/N)"

        if ($addToTrustedRoot -ieq "y")
        {
            $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
            $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath\add-to-trusted-root.ps1`" -certPfxPath `"$certPfxPath`" -pfxPassword `"$pfxPassword`""

            if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))
            {
                Write-Host "Elevating to install certificate into Trusted Root..."
                Start-Process PowerShell -ArgumentList $arguments -Verb RunAs
                exit
            }
            else
            {
                Write-Host "Running Trusted Root installation..."
                & PowerShell -ExecutionPolicy Bypass -File "$scriptPath\add-to-trusted-root.ps1" -certPfxPath "$certPfxPath" -pfxPassword "$pfxPassword"
            }
        }
        else
        {
            Write-Host "Skipping Trusted Root installation."
        }
    }

}
