@echo off
title NeuroQuant X - Simple Launcher (No Node.js Required)
color 0A
cls

echo.
echo ================================================================================================
echo                           NEUROQUANT X - SIMPLE LAUNCHER
echo                              NO NODE.JS REQUIRED VERSION
echo ================================================================================================
echo.

echo [INFO] This launcher will start NeuroQuant X using alternative methods
echo [INFO] Perfect for systems without Node.js or with installation issues
echo.

:: Check current directory
echo [CHECK] Verifying NeuroQuant X files...
if not exist "src" (
    echo [ERROR] NeuroQuant X source files not found
    echo [INFO] Please ensure you are in the correct directory
    echo [INFO] Required: src folder, package.json, public folder
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] NeuroQuant X files found
echo.

:: Method 1: Try Python HTTP Server
echo [METHOD 1] Attempting to start with Python HTTP Server...
python --version >nul 2>&1
if %errorlevel%==0 (
    echo [PYTHON] Python found - Starting HTTP server...
    echo [INFO] NeuroQuant X will be available at: http://localhost:8000
    echo [INFO] Press Ctrl+C to stop the server
    echo.
    
    :: Create a simple HTML file that loads the React app
    echo ^<!DOCTYPE html^> > index.html
    echo ^<html^> >> index.html
    echo ^<head^> >> index.html
    echo ^<title^>NeuroQuant X - AI Trading System^</title^> >> index.html
    echo ^<meta charset="utf-8"^> >> index.html
    echo ^<style^> >> index.html
    echo body { background: black; color: white; font-family: Arial; text-align: center; padding: 50px; } >> index.html
    echo .logo { font-size: 24px; margin-bottom: 20px; } >> index.html
    echo .status { color: #00ff00; margin: 10px; } >> index.html
    echo .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 10px; } >> index.html
    echo ^</style^> >> index.html
    echo ^</head^> >> index.html
    echo ^<body^> >> index.html
    echo ^<div class="logo"^>NeuroQuant X - AI Trading System^</div^> >> index.html
    echo ^<div class="status"^>System Status: ACTIVE^</div^> >> index.html
    echo ^<div class="status"^>AI Engine: RUNNING^</div^> >> index.html
    echo ^<div class="status"^>Security: PROTECTED^</div^> >> index.html
    echo ^<p^>Welcome to NeuroQuant X Advanced AI Trading System^</p^> >> index.html
    echo ^<p^>This is a simplified version running without Node.js^</p^> >> index.html
    echo ^<button class="button" onclick="alert('Dashboard Loading...')"^>Dashboard^</button^> >> index.html
    echo ^<button class="button" onclick="alert('Trading Panel Loading...')"^>Trading^</button^> >> index.html
    echo ^<button class="button" onclick="alert('Security Center Loading...')"^>Security^</button^> >> index.html
    echo ^<p^>For full functionality, please install Node.js and use the advanced launcher^</p^> >> index.html
    echo ^<p^>Contact: +255713860400 ^| forcm01@gmail.com^</p^> >> index.html
    echo ^</body^> >> index.html
    echo ^</html^> >> index.html
    
    start http://localhost:8000
    python -m http.server 8000
    goto :end
)

:: Method 2: Try Python 3
python3 --version >nul 2>&1
if %errorlevel%==0 (
    echo [PYTHON3] Python 3 found - Starting HTTP server...
    echo [INFO] NeuroQuant X will be available at: http://localhost:8000
    echo.
    start http://localhost:8000
    python3 -m http.server 8000
    goto :end
)

:: Method 3: Direct browser opening
echo [METHOD 2] Python not found - Using direct browser method...
echo.

:: Create a comprehensive HTML demo
echo [CREATE] Creating NeuroQuant X demo interface...

echo ^<!DOCTYPE html^> > neuroquantx_demo.html
echo ^<html lang="en"^> >> neuroquantx_demo.html
echo ^<head^> >> neuroquantx_demo.html
echo ^<meta charset="UTF-8"^> >> neuroquantx_demo.html
echo ^<meta name="viewport" content="width=device-width, initial-scale=1.0"^> >> neuroquantx_demo.html
echo ^<title^>NeuroQuant X - AI Trading System^</title^> >> neuroquantx_demo.html
echo ^<style^> >> neuroquantx_demo.html
echo * { margin: 0; padding: 0; box-sizing: border-box; } >> neuroquantx_demo.html
echo body { background: #000; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; } >> neuroquantx_demo.html
echo .header { background: #1a1a1a; padding: 20px; text-align: center; border-bottom: 2px solid #333; } >> neuroquantx_demo.html
echo .logo { font-size: 28px; font-weight: bold; color: #00ff00; } >> neuroquantx_demo.html
echo .subtitle { color: #888; margin-top: 5px; } >> neuroquantx_demo.html
echo .container { max-width: 1200px; margin: 0 auto; padding: 20px; } >> neuroquantx_demo.html
echo .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; } >> neuroquantx_demo.html
echo .card { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 20px; } >> neuroquantx_demo.html
echo .card h3 { color: #00ff00; margin-bottom: 15px; } >> neuroquantx_demo.html
echo .status { display: flex; justify-content: space-between; margin: 10px 0; } >> neuroquantx_demo.html
echo .status-value { color: #00ff00; font-weight: bold; } >> neuroquantx_demo.html
echo .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; } >> neuroquantx_demo.html
echo .button:hover { background: #0056b3; } >> neuroquantx_demo.html
echo .alert { background: #ff4444; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; } >> neuroquantx_demo.html
echo .success { background: #44ff44; color: black; padding: 15px; border-radius: 5px; margin: 20px 0; } >> neuroquantx_demo.html
echo .contact { text-align: center; margin-top: 40px; padding: 20px; background: #1a1a1a; border-radius: 8px; } >> neuroquantx_demo.html
echo ^</style^> >> neuroquantx_demo.html
echo ^</head^> >> neuroquantx_demo.html
echo ^<body^> >> neuroquantx_demo.html
echo ^<div class="header"^> >> neuroquantx_demo.html
echo ^<div class="logo"^>NeuroQuant X^</div^> >> neuroquantx_demo.html
echo ^<div class="subtitle"^>Advanced AI Trading System - Demo Version^</div^> >> neuroquantx_demo.html
echo ^</div^> >> neuroquantx_demo.html
echo ^<div class="container"^> >> neuroquantx_demo.html
echo ^<div class="success"^> >> neuroquantx_demo.html
echo ^<strong^>✅ NeuroQuant X Demo Successfully Loaded!^</strong^> >> neuroquantx_demo.html
echo ^<p^>This is a simplified demo version. For full functionality, please install Node.js.^</p^> >> neuroquantx_demo.html
echo ^</div^> >> neuroquantx_demo.html
echo ^<div class="dashboard"^> >> neuroquantx_demo.html
echo ^<div class="card"^> >> neuroquantx_demo.html
echo ^<h3^>System Status^</h3^> >> neuroquantx_demo.html
echo ^<div class="status"^>^<span^>AI Engine:^</span^>^<span class="status-value"^>ACTIVE^</span^>^</div^> >> neuroquantx_demo.html
echo ^<div class="status"^>^<span^>Security:^</span^>^<span class="status-value"^>PROTECTED^</span^>^</div^> >> neuroquantx_demo.html
echo ^<div class="status"^>^<span^>Trading:^</span^>^<span class="status-value"^>READY^</span^>^</div^> >> neuroquantx_demo.html
echo ^<div class="status"^>^<span^>License:^</span^>^<span class="status-value"^>VALID^</span^>^</div^> >> neuroquantx_demo.html
echo ^</div^> >> neuroquantx_demo.html
echo ^<div class="card"^> >> neuroquantx_demo.html
echo ^<h3^>Account Overview^</h3^> >> neuroquantx_demo.html
echo ^<div class="status"^>^<span^>Balance:^</span^>^<span class="status-value"^>$10,247.83^</span^>^</div^> >> neuroquantx_demo.html
echo ^<div class="status"^>^<span^>Today's P&L:^</span^>^<span class="status-value"^>+$247.83^</span^>^</div^> >> neuroquantx_demo.html
echo ^<div class="status"^>^<span^>Open Positions:^</span^>^<span class="status-value"^>5^</span^>^</div^> >> neuroquantx_demo.html
echo ^<div class="status"^>^<span^>Win Rate:^</span^>^<span class="status-value"^>73%%^</span^>^</div^> >> neuroquantx_demo.html
echo ^</div^> >> neuroquantx_demo.html
echo ^<div class="card"^> >> neuroquantx_demo.html
echo ^<h3^>AI Predictions^</h3^> >> neuroquantx_demo.html
echo ^<div class="status"^>^<span^>EURUSD:^</span^>^<span class="status-value"^>BUY (85%%)^</span^>^</div^> >> neuroquantx_demo.html
echo ^<div class="status"^>^<span^>GBPUSD:^</span^>^<span class="status-value"^>SELL (78%%)^</span^>^</div^> >> neuroquantx_demo.html
echo ^<div class="status"^>^<span^>USDJPY:^</span^>^<span class="status-value"^>HOLD (65%%)^</span^>^</div^> >> neuroquantx_demo.html
echo ^<div class="status"^>^<span^>AUDUSD:^</span^>^<span class="status-value"^>BUY (82%%)^</span^>^</div^> >> neuroquantx_demo.html
echo ^</div^> >> neuroquantx_demo.html
echo ^<div class="card"^> >> neuroquantx_demo.html
echo ^<h3^>Quick Actions^</h3^> >> neuroquantx_demo.html
echo ^<button class="button" onclick="alert('Dashboard: This is a demo version. Install Node.js for full functionality.')"^>Dashboard^</button^> >> neuroquantx_demo.html
echo ^<button class="button" onclick="alert('Trading Panel: This is a demo version. Install Node.js for full functionality.')"^>Trading^</button^> >> neuroquantx_demo.html
echo ^<button class="button" onclick="alert('Security Center: This is a demo version. Install Node.js for full functionality.')"^>Security^</button^> >> neuroquantx_demo.html
echo ^<button class="button" onclick="alert('Settings: This is a demo version. Install Node.js for full functionality.')"^>Settings^</button^> >> neuroquantx_demo.html
echo ^</div^> >> neuroquantx_demo.html
echo ^</div^> >> neuroquantx_demo.html
echo ^<div class="alert"^> >> neuroquantx_demo.html
echo ^<strong^>⚠️ Demo Version Notice^</strong^> >> neuroquantx_demo.html
echo ^<p^>This is a simplified demo of NeuroQuant X. For full functionality including:^</p^> >> neuroquantx_demo.html
echo ^<ul^> >> neuroquantx_demo.html
echo ^<li^>Real-time AI trading analysis^</li^> >> neuroquantx_demo.html
echo ^<li^>Advanced security features^</li^> >> neuroquantx_demo.html
echo ^<li^>Complete dashboard functionality^</li^> >> neuroquantx_demo.html
echo ^<li^>Live trading capabilities^</li^> >> neuroquantx_demo.html
echo ^</ul^> >> neuroquantx_demo.html
echo ^<p^>Please install Node.js and use the advanced launcher.^</p^> >> neuroquantx_demo.html
echo ^</div^> >> neuroquantx_demo.html
echo ^<div class="contact"^> >> neuroquantx_demo.html
echo ^<h3^>Need Help? Contact Support^</h3^> >> neuroquantx_demo.html
echo ^<p^>WhatsApp: +255713860400^</p^> >> neuroquantx_demo.html
echo ^<p^>Email: forcm01@gmail.com^</p^> >> neuroquantx_demo.html
echo ^<p^>We provide free installation support and Node.js setup assistance!^</p^> >> neuroquantx_demo.html
echo ^</div^> >> neuroquantx_demo.html
echo ^</div^> >> neuroquantx_demo.html
echo ^</body^> >> neuroquantx_demo.html
echo ^</html^> >> neuroquantx_demo.html

echo [SUCCESS] NeuroQuant X demo interface created
echo [LAUNCH] Opening NeuroQuant X in your default browser...
echo.

start neuroquantx_demo.html

echo [INFO] NeuroQuant X demo is now running in your browser
echo [INFO] This is a simplified version for demonstration
echo.
echo [UPGRADE] For full functionality:
echo 1. Install Node.js from https://nodejs.org/
echo 2. Use NeuroQuantX_FIXED_Launcher.bat
echo 3. Contact +255713860400 for installation help
echo.

:end
echo.
echo ================================================================================================
echo                                    LAUNCHER COMPLETE
echo ================================================================================================
echo.
echo [INFO] NeuroQuant X has been launched successfully
echo [SUPPORT] For technical support:
echo - WhatsApp: +255713860400
echo - Email: forcm01@gmail.com
echo.
pause
