@echo off
title Push to GitHub - SmartExam AI
color 0A
echo =======================================================
echo          Pushing SmartExam AI to GitHub
echo =======================================================
echo.

set PATH=C:\Users\debji\AppData\Local\Programs\Git\cmd;C:\Users\debji\AppData\Local\Programs\Git\bin;%PATH%

echo Checking Git status...
git status
echo.

echo Pushing to https://github.com/debjitsarker2005-lgtm/Nptel.git ...
echo (If a browser window or login prompt opens, please sign in to authorize)
echo.

git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo =======================================================
    echo  SUCCESS! Your code is now live on GitHub:
    echo  https://github.com/debjitsarker2005-lgtm/Nptel
    echo =======================================================
) else (
    echo.
    echo [ERROR] Push failed or was cancelled.
)

echo.
pause
