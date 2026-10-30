@echo off
chcp 65001 >nul
title KET NOI PUBLIC 4G - AIRSENSE AI
echo ======================================================================
echo   DANG TAO DUONG LINK CONG KHAI CHO DIEN THOAI (4G / 5G / KHAC MANG)...
echo ======================================================================
echo.
cd /d "%~dp0"
cloudflared.exe tunnel --url http://127.0.0.1:8000
pause
