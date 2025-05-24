#!/bin/bash

# GitLab Analysis Tool - Quick Setup Script
# This script helps you set up the GitLab Analysis Tool quickly

echo "=================================================="
echo "GitLab Analysis Tool - Quick Setup"
echo "Repository: https://github.com/pouladzade/gitlab-analysis"
echo "=================================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3.8+."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate || source .venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create configuration from template
if [ ! -f ".env" ]; then
    echo "⚙️ Creating configuration file..."
    cp config/env.template .env
    echo "✓ Configuration file created: .env"
    echo "❗ Please edit .env file and set your GITLAB_TOKEN"
else
    echo "✓ Configuration file already exists"
fi

# Create projects directory
if [ ! -d "projects" ]; then
    mkdir -p projects
    echo "✓ Projects directory created"
else
    echo "✓ Projects directory already exists"
fi

# Create reports directory
if [ ! -d "gitlab_reports" ]; then
    mkdir -p gitlab_reports
    echo "✓ Reports directory created"
else
    echo "✓ Reports directory already exists"
fi

echo
echo "=================================================="
echo "🎉 Setup Complete!"
echo "=================================================="
echo
echo "Next steps:"
echo "1. Edit .env file and set your GITLAB_TOKEN:"
echo "   - Go to GitLab → Profile → Access Tokens"
echo "   - Create token with 'api' and 'read_repository' scopes"
echo "   - Set GITLAB_TOKEN in .env file"
echo
echo "2. Clone your GitLab repositories to projects/ directory:"
echo "   cd projects"
echo "   git clone your-repo-urls..."
echo
echo "3. Test your setup:"
echo "   python gitlab_analysis.py --help"
echo
echo "4. Start analyzing:"
echo "   python gitlab_analysis.py analyze --days 30"
echo
echo "For detailed documentation, see README.md"
echo "Repository: https://github.com/pouladzade/gitlab-analysis"
echo 