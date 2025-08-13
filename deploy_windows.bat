@echo off
echo 🚀 DigitalOcean App Platform Deployment for Windows
echo ===================================================

echo.
echo 📋 Prerequisites Check:
echo.

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git is not installed. Please install Git first.
    echo    Download from: https://git-scm.com/download/win
    pause
    exit /b 1
) else (
    echo ✅ Git is installed
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python first.
    echo    Download from: https://python.org/downloads
    pause
    exit /b 1
) else (
    echo ✅ Python is installed
)

echo.
echo 🔧 Setup Steps:
echo.

echo 1. Push your code to GitHub repository
echo 2. Update .do/app.yaml with your repository details
echo 3. Go to DigitalOcean App Platform console
echo 4. Create new app from GitHub repository
echo 5. Set environment variables
echo 6. Deploy!
echo.

echo 📚 For detailed instructions, see PRODUCTION_SETUP.md
echo.

echo 🚀 Ready to deploy? Open your browser and go to:
echo    https://cloud.digitalocean.com/apps
echo.

pause
