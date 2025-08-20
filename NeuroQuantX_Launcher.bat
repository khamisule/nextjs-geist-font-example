@echo off
title NeuroQuant X - AI Trading System Launcher
color 0A

echo.
echo  ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗  ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗    ██╗  ██╗
echo  ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝    ╚██╗██╔╝
echo  ██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║██║   ██║██║   ██║███████║██╔██╗ ██║   ██║        ╚███╔╝ 
echo  ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██║   ██║██║   ██║██╔══██║██║╚██╗██║   ██║        ██╔██╗ 
echo  ██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║       ██╔╝ ██╗
echo  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝       ╚═╝  ╚═╝
echo.
echo                                    AI TRADING SYSTEM - PROFESSIONAL EDITION
echo                                           Developed for 24/7 Trading Operations
echo.
echo ================================================================================================
echo.

:: Check if Node.js is installed
echo [INFO] Checking system requirements...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo [INFO] Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

:: Check if npm is available
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not available
    echo [INFO] Please ensure npm is installed with Node.js
    pause
    exit /b 1
)

echo [SUCCESS] Node.js and npm are available
echo.

:: Check if we're in the correct directory
if not exist "package.json" (
    echo [ERROR] package.json not found
    echo [INFO] Please run this launcher from the NeuroQuant X root directory
    pause
    exit /b 1
)

echo [INFO] Initializing NeuroQuant X Trading System...
echo.

:: Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo [INFO] Installing dependencies for first-time setup...
    echo [INFO] This may take a few minutes...
    npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed successfully
    echo.
)

:: Kill any existing processes on port 8000
echo [INFO] Checking for existing processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo [INFO] Terminating existing process %%a on port 8000...
    taskkill /f /pid %%a >nul 2>&1
)

echo [INFO] Starting NeuroQuant X AI Trading System...
echo [INFO] System will be available at: http://localhost:8000
echo [INFO] Press Ctrl+C to stop the system
echo.
echo ================================================================================================
echo                                    SYSTEM STATUS: INITIALIZING
echo ================================================================================================
echo.

:: Start the development server
set PORT=8000
npm run dev

:: If we get here, the server has stopped
echo.
echo ================================================================================================
echo                                    SYSTEM STATUS: STOPPED
echo ================================================================================================
echo.
echo [INFO] NeuroQuant X has been stopped
echo [INFO] Thank you for using NeuroQuant X AI Trading System
pause
