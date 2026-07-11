@echo off
rem ============================================================
rem  extract_tw_pack.bat  –  RPFM CLI helper for WH3 .pack files
rem ============================================================

::--- 1. sanity-check -------------------------------------------------------
if "%~1"=="" (
    echo ^>^> Usage: %~nx0 ^<PACK_BASE_NAME^>
    echo ^>^> Example: %~nx0 !vassal_the_counts_tow
    exit /b 1
)

::--- 2. configurable paths -------------------------------------------------
set "RPFM_EXE=D:\modding\rpfm-v4.3.14\rpfm_cli.exe"
set "GAME_DATA=D:\Games\Steam\steamapps\common\Total War WARHAMMER III\data"
set "SCHEMA=D:\modding\rpfm-schemas\schema_wh3.ron"

::--- 3. derived variables --------------------------------------------------
set "PACK=%~1"
set "PACK_FILE=%GAME_DATA%\%PACK%.pack"
set "OUT_DIR=%PACK%"
set "OUT_FILTER=/;.\%PACK%"

::--- 4. prepare output folder ----------------------------------------------
if exist "%OUT_DIR%" (
    echo ^>^> Output folder "%OUT_DIR%" exists. Deleting...
    rmdir /s /q "%OUT_DIR%"
)

echo ^>^> Creating fresh output folder "%OUT_DIR%"...
mkdir "%OUT_DIR%"

::--- 5. run the extractor --------------------------------------------------
echo.
echo Extracting "%PACK_FILE%" ...
"%RPFM_EXE%" --game warhammer_3 pack extract ^
    -p "%PACK_FILE%" ^
    -F "%OUT_FILTER%" ^
    -t "%SCHEMA%" || (
        echo ^>^> Extraction failed.
        exit /b 1
)

echo ^>^> Done – files are in ".\%OUT_DIR%\".
