@echo off

:: wait for system to bootup
timeout /t 40

:: storage engine
:: wsl -- bash -c "nohup /usr/bin/redis-server 0.0.0.0:6379"
wsl --exec dbus-launch true

set "APP_DIR=c:\hm"

:: cleanup old app files
del /q "%APP_DIR%\*"
FOR /D %%p IN ("%APP_DIR%\*.*") DO rmdir "%%p" /s /q

:: unpack to input cli
"%~dp0\input.exe"

:: start app
:: set HM_LOG_FILE=z:\share\logs\herominer.log
set HM_CONFIG_DIR=z:\app\config
set HM_ENTRYPOINT_PATH=%APP_DIR%\cli\input.exe

"%~dp0\cli.exe" daemon start

:: "%~dp0\app.exe" --log-file "z:\herowars\logs\herominer.log" --driver-path "m:\driver\MacroRecorder\MacroRecorder.exe" --data-dir "m:\data" --share-dir "m:\persist" daemon start

pause