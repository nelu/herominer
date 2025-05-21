# Define parameters
param(
    [string]$certPfxPath = "myapp.pfx",
    [string]$pfxPassword = "MyStrongPassword"
)

# Ensure the script runs as Administrator (UAC Prompt)
$scriptPath = $MyInvocation.MyCommand.Definition
$arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`" -certPfxPath `"$certPfxPath`" -pfxPassword `"$pfxPassword`""

If (-Not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires administrator privileges. Restarting with elevated permissions..." -ForegroundColor Yellow
    Start-Process PowerShell -ArgumentList $arguments -Verb RunAs
    Exit  # Prevent the non-admin process from continuing
}


# Check if certificate file exists
if ([string]::IsNullOrEmpty($certPfxPath) -or !(Test-Path $certPfxPath)) {
    Write-Host "Error: Certificate file not found at $certPfxPath" -ForegroundColor Red
    exit 1
}

# Import the certificate into Trusted Root Authorities
Write-Host "Adding certificate to Trusted Root Authorities..."
Import-PfxCertificate -FilePath $certPfxPath -CertStoreLocation Cert:\LocalMachine\Root -Password (ConvertTo-SecureString -String $pfxPassword -Force -AsPlainText)

Write-Host "Certificate successfully added to Trusted Root Authorities!" -ForegroundColor Green
