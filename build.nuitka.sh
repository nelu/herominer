#!/usr/bin/env bash
set -e
#set -x  # Echo every command as it's executed

export PATH="/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.39.33519/bin/Hostx64/x64:/c/Program Files (x86)/Windows Kits/10/bin/10.0.22621.0/x64:$PATH"

printenv

APP_VERSION="${APP_VERSION:-1.0.0}"
CERT_PASS="${CERT_PASS:-MyStrongPassword}"
SEVEN_ZIP="${SEVEN_ZIP:-/c/Program Files/7-Zip/7z.exe}"

PUBLISH_DIR="./dev"
RELEASE_DIR="./release"
SFX_MODULE="./sources/7zsd_All_x64.sfx"

# Read input binary path from config
INPUT_CLI_PATH=$(dirname "$(cat ./app/config/cli.path)")

PUBLISH_DIR=./"dev"
RELEASE_DIR=./"release"


# pyinstaller --noconfirm  --onedir --version-file ./version.txt --hide-console hide-late --distpath ./scripts/ ./app/cli.py \

# --mingw64 --show-progress \
#  --mingw64 --clang \
#  --static-libpython=yes \
#  --lto=yes \#
# --disable-console
# Windows specific controls:
#
#  --remove-output \

#  --include-data-dir=./data=data/ \
#  --include-module=app.web \
#  --include-module=app.web.heromanager \
#  --module-parameter=django-settings-module=app.web.heromanager.settings \
#   --include-data-files=$(python -c "import seleniumwire, os; print(os.path.join(seleniumwire.__path__[0], 'ca.crt'))")=seleniumwire/ca.crt \
#
#   --include-data-dir="${RELEASE_DIR}/cli/inputs.dist"=cli \
#  --onefile-tempdir-spec="z:\app" \


build_sfx_installer() {
  local DIST_DIR="$(realpath "$1")"   # e.g., /abs/path/to/release/input.dist

  # === Derived names and paths ===
  local DIST_BASENAME
  DIST_BASENAME=$(basename "$DIST_DIR")                # → input.dist
  local BASE_NAME="${DIST_BASENAME%.dist}"             # → input

  local OUTPUT_DIR
  OUTPUT_DIR=$(dirname "$DIST_DIR")                    # → ./release

  local ARCHIVE_PATH="${OUTPUT_DIR}/${DIST_BASENAME}.7z"   # → ./release/input.dist.7z
  local SFX_OUTPUT="${OUTPUT_DIR}/${BASE_NAME}.exe"        # → ./release/input.exe
  local PAYLOAD_EXE="${DIST_DIR}/${BASE_NAME}.exe"         # → ./release/input.dist/input.exe

  echo "🔏 Signing internal: $PAYLOAD_EXE"
  ./scripts/selfsign.ps1 -exeToSign "$PAYLOAD_EXE" \
    -certPfxPath ./config/myapp.pfx \
    -pfxPassword "$CERT_PASS" || return 1

  echo "📦 Creating archive: $ARCHIVE_PATH"
  rm -f "$ARCHIVE_PATH" || return 1
  "$SEVEN_ZIP" a -r -bb1 -bsp1 "$ARCHIVE_PATH" "$DIST_DIR"/* "$DIST_DIR"/.* || return 1

  echo "📤 Building SFX: $SFX_OUTPUT"
  cat "$SFX_MODULE" ./config/sfx.txt "$ARCHIVE_PATH" > "$SFX_OUTPUT" || return 1

  echo "🔏 Signing final SFX: $SFX_OUTPUT"
  ./scripts/selfsign.ps1 -exeToSign "$SFX_OUTPUT" \
    -certPfxPath ./config/myapp.pfx \
    -pfxPassword "$CERT_PASS" || return 1

  echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ Done! Created in ${OUTPUT_DIR}:"
  echo "   - Archive: $(basename "$ARCHIVE_PATH")"
  echo "   - SFX EXE: $(basename "$SFX_OUTPUT")"
  echo "   - Internal EXE: $(basename "$PAYLOAD_EXE")"
}

echo "$(date '+%Y-%m-%d %H:%M:%S') - Building release: cli.exe and input.exe"


python.exe -m nuitka --standalone \
  --assume-yes-for-downloads \
  --include-data-files=./config/cli.env=.env \
  --noinclude-pytest-mode=nofollow \
  --nofollow-import-to=selenium,seleniumwire,app.game,app.driver,app.tasks,app.management,app.tests,app.web,app.daemon \
  --onefile-tempdir-spec="$INPUT_CLI_PATH" \
  --company-name="AutoWeb LTD" \
  --file-version="${APP_VERSION}" \
  --product-version="${APP_VERSION}" \
  --file-description="HeroMiner Input Cli" \
  --copyright="All rights reserved © TheNet" \
  --trademarks="AutoWeb TheNet" \
  --windows-console-mode=attach \
  --windows-icon-from-ico=./sources/herominer-icon.ico \
  --output-dir="$RELEASE_DIR" \
  --include-package=app \
  ./app/input.py \
  && \
 build_sfx_installer "./release/input.dist" && \
\
python.exe -m nuitka --standalone \
  --onefile \
  --include-data-files=./config/app.env=.env \
  --include-data-dir=./app/config=config \
  --noinclude-pytest-mode=nofollow \
  --nofollow-import-to=app.tests \
  --include-data-files=./config/ca.crt=config/ca.crt \
  --include-data-files=./config/ca.key=config/ca.key \
  --company-name="AutoWeb LTD" \
  --file-version="${APP_VERSION}" \
  --product-version="${APP_VERSION}" \
  --file-description="HeroMiner bundle launcher" \
  --copyright="All rights reserved © TheNet" \
  --trademarks="AutoWeb TheNet" \
  --windows-console-mode=attach \
  --windows-icon-from-ico=./sources/herominer-icon.ico \
  --output-dir="$RELEASE_DIR" \
  --include-package=app \
  --onefile-tempdir-spec="c:\hm\app" \
  ./app/cli.py #
  # \
#&& \
#build_sfx_installer "./release/cli.dist" && \

cp -rfp ./scripts/run*.cmd "${RELEASE_DIR}/" && \
 ./scripts/selfsign.ps1 -exeToSign "./release/cli.exe" \
    -certPfxPath ./config/myapp.pfx \
    -pfxPassword "$CERT_PASS"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Done build ./release/cli.exe"

#rm -rf "${PUBLISH_DIR}"/{*,.*} && mkdir -p "${PUBLISH_DIR}" && \
#cp -arfp "${RELEASE_DIR}"/cli.dist/.  "${PUBLISH_DIR}/"
