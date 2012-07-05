@echo off

del /f /q cycle_submit.exe
python setup.py py2exe
move dist\cycle_submit.exe .
rmdir /s /q build
rmdir /s /q dist

echo.
echo.
echo cycle_submit.exe has been built successfully
echo.