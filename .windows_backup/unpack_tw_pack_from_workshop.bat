@echo off
rem ============================================================
rem  extract_tw_pack.bat – Auto-detect packfile in given folder
rem ============================================================

::--- 1. sanity-check -------------------------------------------------------
if "%~1"=="" (
    echo ^>^> Usage: %~nx0 ^<FOLDER_CONTAINING_PACKFILE^>
    echo ^>^> Example: %~nx0 "D:\Games\Steam\steamapps\workshop\content\1142710\3532864014"
    exit /b 1
)

set "PACK_FOLDER=%~1"

::--- 2. find .pack file in folder -----------------------------------------
for %%f in ("%PACK_FOLDER%\*.pack") do (
    set "PACK_FILE=%%f"
    goto :found
)

echo ^>^> ERROR: No .pack file found in folder "%PACK_FOLDER%"
exit /b 1

:found

::--- 3. get file name without path or extension ---------------------------
for %%f in ("%PACK_FILE%") do (
    set "PACK_NAME=%%~nf"
)

::--- 4. configurable paths ------------------------------------------------
set "RPFM_EXE=D:\modding\rpfm-v4.3.14\rpfm_cli.exe"
set "SCHEMA=D:\modding\rpfm-schemas\schema_wh3.ron"

::--- 5. prepare output folder ---------------------------------------------
if exist "%PACK_NAME%" (
    echo ^>^> Output folder "%PACK_NAME%" exists. Deleting...
    rmdir /s /q "%PACK_NAME%"
)

echo ^>^> Creating fresh output folder "%PACK_NAME%"...
mkdir "%PACK_NAME%"

::--- 6. run the extractor -------------------------------------------------
echo.
echo Extracting "%PACK_FILE%" ...
"%RPFM_EXE%" --game warhammer_3 pack extract ^
    -p "%PACK_FILE%" ^
    -F "/;.\%PACK_NAME%" ^
    -t "%SCHEMA%" || (
        echo ^>^> Extraction failed.
        exit /b 1
)

echo ^>^> Done – files are in ".\%PACK_NAME%\".
