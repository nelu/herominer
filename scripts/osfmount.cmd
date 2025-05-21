@echo off
set OSFMountPath="C:\Program Files\OSFMount\OSFMount.com"
set ImagePath="\\vmware-host\Shared Folders\herowars\bins\game_image.img"
set DriveLetter=M:

:: Check arguments
if "%1"=="-mount" goto :MOUNT
if "%1"=="-save" goto :SAVE
if "%1"=="-setup" goto :SETUP
echo Invalid argument. Use:
echo - setup (registers startup and shutdown tasks)
echo - mount (mounts the RAM disk)
echo - save (saves the RAM disk)
exit /b 1

:: Mount RAM Disk Function
:MOUNT
echo Mounting RAM disk on %DriveLetter%...
%OSFMountPath% -a -t file -o rw -f %ImagePath% -m %DriveLetter%
:: Check if the command was successful
if %ERRORLEVEL% == 0 (
    echo RAM disk mounted successfully on %DriveLetter%.
    pause
) else (
    echo Failed to mount RAM disk. Error code: %ERRORLEVEL%
)
exit /b 0

:: Save RAM Disk Function
:SAVE
echo Saving RAM disk on %DriveLetter% before shutdown...
%OSFMountPath% -d -m %DriveLetter%
:: Check if dismount was successful
if %ERRORLEVEL% == 0 (
    echo RAM disk dismounted successfully.
) else (
    echo Failed to dismount RAM disk. Error code: %ERRORLEVEL%
)
:: %OSFMountPath% -s -m %DriveLetter% -f %ImagePath%
exit /b 0

:: Setup Tasks in Task Scheduler
:SETUP
echo Registering startup task...
schtasks /create /tn "MountRAMDisk" /tr "%~dp0manage_ram.cmd -mount" /sc onstart /ru SYSTEM /RL HIGHEST /f

echo Registering shutdown task...
schtasks /create /tn "SaveRAMDisk" /tr "%~dp0manage_ramdisk.cmd -save" /sc onlogoff /ru SYSTEM /RL HIGHEST /f

echo Setup complete! RAM disk will auto-mount at startup and save before shutdown.
exit /b 0
