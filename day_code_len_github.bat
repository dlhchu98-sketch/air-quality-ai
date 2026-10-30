@echo off
chcp 65001 >nul
title DAY CODE LEN GITHUB PAGES
echo ======================================================================
echo   DANG DAY CODE LEN GITHUB DE CO LINK 24/7 (TAT MAY TINH VAN XEM DUOC)...
echo ======================================================================
echo.
cd /d "%~dp0"
git remote remove origin 2>nul
git remote add origin https://github.com/dlhchu98-sketch/air-quality-ai.git
git branch -M master
git push -u origin master
echo.
echo ======================================================================
echo   DA DAY CODE LEN GITHUB THANH CONG!
echo   Link web vinh vien cua ban: https://dlhchu98-sketch.github.io/air-quality-ai/
echo ======================================================================
pause
