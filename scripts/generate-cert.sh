#!/usr/bin/env bash
set -e

# Set defaults
CERT_NAME="${CERT_NAME:-HeroMiner Signing Cert}"
CERT_DIR="${CERT_DIR:-./config}"
CERT_PASS="${CERT_PASS:-MyStrongPassword}"

PFX_PATH="$CERT_DIR/myapp.pfx"
KEY_PATH="$CERT_DIR/ca.key"
CRT_PATH="$CERT_DIR/ca.crt"
PEM_PATH="$CERT_DIR/cert.pem"

# Create output directory
mkdir -p "$CERT_DIR"

echo "[+] Generating private key..."
openssl genrsa -out "$KEY_PATH" 2048

echo "[+] Creating self-signed certificate..."
openssl req -new -x509 \
  -key "$KEY_PATH" \
  -out "$PEM_PATH" \
  -days 730 \
  -subj "//CN=${CERT_NAME}"

echo "[+] Exporting certificate to PFX..."
openssl pkcs12 -export \
  -out "$PFX_PATH" \
  -inkey "$KEY_PATH" \
  -in "$PEM_PATH" \
  -passout pass:"$CERT_PASS"

echo "[+] Extracting certificate (.crt) from PFX..."
openssl pkcs12 -in "$PFX_PATH" \
  -clcerts -nokeys \
  -passin pass:"$CERT_PASS" \
  -out "$CRT_PATH"

echo "[+] Removing passphrase from private key..."
openssl rsa -in "$KEY_PATH" -out "$KEY_PATH.tmp"
mv "$KEY_PATH.tmp" "$KEY_PATH"

echo "[*] Certificate generation complete."
echo "    - PFX: $PFX_PATH"
echo "    - CRT: $CRT_PATH"
echo "    - KEY: $KEY_PATH"
