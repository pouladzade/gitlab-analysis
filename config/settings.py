#!/usr/bin/env python3
"""
GitLab Analysis Tool - Configuration Settings

This module manages configuration settings for the GitLab analysis tools.
It loads settings from environment variables with sensible defaults.
"""

import os
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class GitLabAnalysisConfig:
    """Configuration management for GitLab Analysis Tool."""
    
    def __init__(self):
        """Initialize configuration with environment variables and defaults."""
        
        # GitLab connection settings
        self.gitlab_url = os.getenv('GITLAB_URL', 'https://gitlab.ptc-telematik.de')
        self.gitlab_token = os.getenv('GITLAB_TOKEN')
        
        # Analysis settings
        self.default_analysis_days = int(os.getenv('DEFAULT_ANALYSIS_DAYS', '60'))
        
        # Directory settings
        self.reports_directory = os.getenv('REPORTS_DIRECTORY', 'gitlab_reports')
        self.projects_directory = os.getenv('PROJECTS_DIRECTORY', 'projects')
        
        # File filtering
        default_extensions = '.py,.js,.java,.cpp,.c,.h,.cs,.php,.rb,.go,.ts,.jsx,.vue,.html,.css,.scss,.sql,.yaml,.yml,.json,.xml'
        extensions_str = os.getenv('CODE_FILE_EXTENSIONS', default_extensions)
        self.code_file_extensions = [ext.strip() for ext in extensions_str.split(',')]
        
        # Author filtering
        authors_str = os.getenv('DEFAULT_AUTHORS', '')
        self.default_authors = [author.strip() for author in authors_str.split(',') if author.strip()] if authors_str else []
        
        # Repository exclusions
        exclude_str = os.getenv('EXCLUDE_REPOSITORIES', '')
        self.exclude_repositories = [repo.strip() for repo in exclude_str.split(',') if repo.strip()] if exclude_str else []
        
        # Logging settings
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'gitlab_analysis.log')
        
        # Validate required settings
        self._validate_config()
    
    def _validate_config(self):
        """Validate that required configuration is present."""
        if not self.gitlab_token:
            raise ValueError(
                "GitLab private token not found. Set GITLAB_TOKEN environment variable.\n"
                "You can generate a personal access token in GitLab:\n"
                "  Profile → Access Tokens → Personal Access Tokens\n"
                "  Required scopes: api, read_repository"
            )
    
    def get_projects_path(self) -> Path:
        """Get the projects directory path."""
        return Path.cwd() / self.projects_directory
    
    def get_reports_path(self) -> Path:
        """Get the reports directory path."""
        return Path.cwd() / self.reports_directory
    
    def should_exclude_repository(self, repo_name: str) -> bool:
        """Check if a repository should be excluded from analysis."""
        return repo_name in self.exclude_repositories
    
    def is_code_file(self, file_path: str) -> bool:
        """Check if a file is considered a code file based on extension."""
        return any(file_path.endswith(ext) for ext in self.code_file_extensions)
    
    def get_summary(self) -> dict:
        """Get a summary of current configuration."""
        return {
            'GitLab URL': self.gitlab_url,
            'Token configured': '✓' if self.gitlab_token else '✗',
            'Default analysis days': self.default_analysis_days,
            'Projects directory': self.projects_directory,
            'Reports directory': self.reports_directory,
            'Code file types': len(self.code_file_extensions),
            'Default authors': len(self.default_authors),
            'Excluded repositories': len(self.exclude_repositories),
            'Log level': self.log_level,
        }
    
    def print_summary(self):
        """Print a formatted summary of the configuration."""
        print("GitLab Analysis Tool Configuration")
        print("=" * 50)
        
        summary = self.get_summary()
        for key, value in summary.items():
            print(f"{key:<25}: {value}")
        
        if self.default_authors:
            print(f"\nDefault authors: {', '.join(self.default_authors)}")
        
        if self.exclude_repositories:
            print(f"Excluded repos: {', '.join(self.exclude_repositories)}")
        
        print(f"\nCode file extensions: {', '.join(self.code_file_extensions[:10])}" + 
              (f" (+{len(self.code_file_extensions)-10} more)" if len(self.code_file_extensions) > 10 else ""))


def load_config() -> GitLabAnalysisConfig:
    """Load and return the configuration instance."""
    return GitLabAnalysisConfig()


if __name__ == "__main__":
    # Print configuration summary when run directly
    try:
        config = load_config()
        config.print_summary()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        exit(1) 