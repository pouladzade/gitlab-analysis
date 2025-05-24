@echo off

REM GitLab Analysis Tool - Quick Setup Script (Windows)
REM This script helps you set up the GitLab Analysis Tool quickly on Windows

echo ==================================================
echo GitLab Analysis Tool - Quick Setup
echo Repository: https://github.com/pouladzade/gitlab-analysis
echo ==================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is required but not found. Please install Python 3.8+.
    pause
    exit /b 1
)

echo ✓ Python found
python --version

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create configuration from template
if not exist ".env" (
    echo ⚙️ Creating configuration file...
    copy config\env.template .env
    echo ✓ Configuration file created: .env
    echo ❗ Please edit .env file and set your GITLAB_TOKEN
) else (
    echo ✓ Configuration file already exists
)

REM Create projects directory
if not exist "projects" (
    mkdir projects
    echo ✓ Projects directory created
) else (
    echo ✓ Projects directory already exists
)

REM Create reports directory
if not exist "gitlab_reports" (
    mkdir gitlab_reports
    echo ✓ Reports directory created
) else (
    echo ✓ Reports directory already exists
)

echo.
echo ==================================================
echo 🎉 Setup Complete!
echo ==================================================
echo.
echo Next steps:
echo 1. Edit .env file and set your GITLAB_TOKEN:
echo    - Go to GitLab → Profile → Access Tokens
echo    - Create token with 'api' and 'read_repository' scopes
echo    - Set GITLAB_TOKEN in .env file
echo.
echo 2. Clone your GitLab repositories to projects\ directory:
echo    cd projects
echo    git clone your-repo-urls...
echo.
echo 3. Test your setup:
echo    python gitlab_analysis.py --help
echo.
echo 4. Start analyzing:
echo    python gitlab_analysis.py analyze --days 30
echo.
echo For detailed documentation, see README.md
echo Repository: https://github.com/pouladzade/gitlab-analysis
echo.
pause 