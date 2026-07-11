@echo off
setlocal

rem ============================================================
rem  extract_all_workshop_mods_to_debug.bat
rem ============================================================

::--- paths ----------------------------------------------------
set "WORKSHOP_DIR=D:\Games\Steam\steamapps\workshop\content\1142710"
set "DESKTOP=%USERPROFILE%\Desktop"
set "DEBUG_DIR=%DESKTOP%\debug"

:: Path to your existing script
set "UNPACK_SCRIPT=%~dp0unpack_tw_pack_from_workshop.bat"

::--- create debug folder -------------------------------------
if not exist "%DEBUG_DIR%" (
    echo Creating debug folder on Desktop...
    mkdir "%DEBUG_DIR%"
)

echo.
echo ============================================================
echo Extracting all workshop mods to:
echo %DEBUG_DIR%
echo ============================================================
echo.

::--- process each workshop mod --------------------------------
for /d %%M in ("%WORKSHOP_DIR%\*") do (
    echo Processing mod folder: %%~nxM

    rem Run extraction INSIDE debug folder
    pushd "%DEBUG_DIR%"
    call "%UNPACK_SCRIPT%" "%%M"
    popd

    echo.
)

echo ============================================================
echo All mods processed.
echo ============================================================
pause
