#!/usr/bin/env python3
"""
GitLab Analysis Tool - Main Entry Point

This script provides a unified interface to all GitLab analysis and export tools.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("GitLab Analysis Tool v1.0.0")
    print("=" * 60)
    print("Comprehensive GitLab repository analysis and issue export")
    print()

def show_help():
    """Show detailed help information."""
    print_banner()
    print("Available Commands:")
    print()
    print("Repository Analysis:")
    print("  analyze           Analyze local GitLab repositories")
    print("                    └─ Output: gitlab_reports/analysis_YYYYMMDD_HHMMSS/")
    print()
    print("Issue Export:")
    print("  export-markdown   Export issues as Markdown files")
    print("                    └─ Output: gitlab_reports/issues_export_YYYYMMDD_HHMMSS/")
    print("  export-csv        Export issues as CSV files")
    print("                    └─ Output: gitlab_reports/issues_csv_YYYYMMDD_HHMMSS/")
    print("  export-jira       Export issues for Jira import")
    print("                    └─ Output: gitlab_reports/jira_YYYYMMDD_HHMMSS/")
    print()
    print("Usage Examples:")
    print("  python gitlab_analysis.py analyze --days 30")
    print("  python gitlab_analysis.py export-csv --days 7")
    print("  python gitlab_analysis.py export-jira --days 60")
    print()
    print("Global Options:")
    print("  --days N          Number of days back to analyze (default: 60)")
    print("  --help            Show this help message")
    print()
    print("Setup:")
    print("  1. Copy config/.env.example to .env")
    print("  2. Set your GITLAB_TOKEN in the .env file")
    print("  3. Ensure your GitLab repositories are cloned in ./projects/")
    print()

def run_script(script_path, args):
    """Run a script with the given arguments."""
    import subprocess
    
    # Build command
    cmd = [sys.executable, script_path] + args
    
    try:
        # Run the script
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e}")
        return e.returncode
    except FileNotFoundError:
        print(f"Script not found: {script_path}")
        return 1

def main():
    parser = argparse.ArgumentParser(
        description="GitLab Analysis Tool - Unified interface",
        add_help=False  # We'll handle help ourselves
    )
    
    parser.add_argument('command', nargs='?', help='Command to run')
    parser.add_argument('--days', type=int, default=60, help='Number of days back to analyze')
    parser.add_argument('--help', action='store_true', help='Show help')
    
    # Parse known args to allow passing through to scripts
    args, unknown_args = parser.parse_known_args()
    
    if args.help or not args.command:
        show_help()
        return 0
    
    # Map commands to scripts
    scripts_dir = Path(__file__).parent / 'scripts'
    command_map = {
        'analyze': scripts_dir / 'analyze_local_repos.py',
        'export-markdown': scripts_dir / 'export_recent_issues.py',
        'export-csv': scripts_dir / 'export_recent_issues_csv.py',
        'export-jira': scripts_dir / 'export_issues_for_jira.py',
    }
    
    if args.command not in command_map:
        print(f"Unknown command: {args.command}")
        print("Run 'python gitlab_analysis.py --help' for available commands")
        return 1
    
    script_path = command_map[args.command]
    
    # Build arguments to pass to the script
    script_args = [f'--days={args.days}']
    script_args.extend(unknown_args)
    
    print_banner()
    print(f"Running: {args.command}")
    print(f"Script: {script_path}")
    print(f"Arguments: {' '.join(script_args)}")
    print()
    
    return run_script(str(script_path), script_args)

if __name__ == "__main__":
    sys.exit(main()) 