@echo off
REM Batch file to convert all .ui files in qt_designer to .py files in qt_generated_code using pyuic

set "SRC_DIR=qt_designer"
set "DST_DIR=qt_generated_code"

if not exist "%DST_DIR%" (
    mkdir "%DST_DIR%"
)

for %%f in ("%SRC_DIR%\*.ui") do (
    echo Converting %%~nxf...
    pyuic5 --from-imports "%%f" -o "%DST_DIR%\%%~nf.py"
)

echo Done.
pause