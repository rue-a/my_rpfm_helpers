@echo off
rem ============================================================
rem repack_tw_pack.bat  –  Rebuilds a WH3 .pack file from a folder
rem ============================================================

::--- 1. sanity-check -------------------------------------------------------
if "%~1"=="" (
    echo ^>^> Usage: %~nx0 ^<PACK_BASE_NAME^>
    echo ^>^> Example: %~nx0 !vassal_the_counts_tow
    exit /b 1
)

::--- 2. configurable paths -------------------------------------------------
set "RPFM_EXE=D:\modding\rpfm-v4.3.14\rpfm_cli.exe"
set "SCHEMA=D:\modding\rpfm-schemas\schema_wh3.ron"
set "OUTPUT_DIR=D:\Games\Steam\steamapps\common\Total War WARHAMMER III\data"

::--- 3. derived variables --------------------------------------------------
set "PACK=%~1"
set "PACK_FILE=%OUTPUT_DIR%\%PACK%.pack"
set "SOURCE_FOLDER=%CD%\%PACK%"

::--- 4. sanity-check: source folder exists ---------------------------------
if not exist "%SOURCE_FOLDER%" (
    echo ^>^> ERROR: Source folder "%SOURCE_FOLDER%" does not exist.
    exit /b 1
)

::--- 5. remove old .pack if it exists --------------------------------------
if exist "%PACK_FILE%" (
    echo ^>^> Existing pack file "%PACK_FILE%" found. Deleting...
    del /f /q "%PACK_FILE%"
)

::--- 6. create empty pack file ---------------------------------------------
echo ^>^> Creating empty pack file "%PACK_FILE%" ...
"%RPFM_EXE%" --game warhammer_3 pack create -p "%PACK_FILE%" || (
    echo ^>^> Failed to create pack file.
    exit /b 1
)

::--- 7. add files from source folder to the pack ---------------------------
echo ^>^> Adding contents of "%SOURCE_FOLDER%" to the pack ...
"%RPFM_EXE%" --game warhammer_3 pack add ^
    -p "%PACK_FILE%" ^
    -t "%SCHEMA%" ^
    -F "%SOURCE_FOLDER%" || (
        echo ^>^> Failed to add files to pack.
        exit /b 1
)

echo ^>^> Done – updated pack: "%PACK_FILE%"
