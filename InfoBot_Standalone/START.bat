@echo off
chcp 65001 >nul
title InfoBot - Telegram Access Bot
color 0A
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║           ЗАПУСК ИНФО-БОТА (INFO BOT)                   ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 🤖 Остановка старых процессов и запуск бота...
powershell -Command "Get-Process python, ngrok -ErrorAction SilentlyContinue | Stop-Process -Force; Start-Sleep -Seconds 2"
python run_info_bot.py
pause




