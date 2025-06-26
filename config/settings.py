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
        
        # Required GitLab settings
        self.gitlab_url = os.getenv('GITLAB_URL')
        self.gitlab_token = os.getenv('GITLAB_TOKEN') or os.getenv('GITLAB_PRIVATE_TOKEN')
        
        if not self.gitlab_url:
            raise ValueError(
                "GITLAB_URL environment variable is required.\n"
                "Please set it in your .env file.\n"
                "Example: GITLAB_URL=https://gitlab.example.com"
            )
        
        if not self.gitlab_token:
            raise ValueError(
                "GITLAB_TOKEN environment variable is required.\n" 
                "Please set your GitLab personal access token in the .env file.\n"
                "You can generate one at: GitLab → Profile → Access Tokens → Personal Access Tokens\n"
                "Required scopes: api, read_repository, read_registry"
            )
        
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
        
        # Output settings
        self.output_directory = os.getenv('OUTPUT_DIRECTORY', 'gitlab_reports')
        self.packages_output_directory = os.getenv('PACKAGES_OUTPUT_DIRECTORY', 'gitlab_packages_report')
        
        # Analysis behavior settings
        self.exclude_merge_commits = os.getenv('EXCLUDE_MERGE_COMMITS', 'true').lower() == 'true'
        self.consolidate_authors = os.getenv('CONSOLIDATE_AUTHORS', 'true').lower() == 'true'
        
        # Performance settings
        self.max_repositories = int(os.getenv('MAX_REPOSITORIES', '100'))
        self.api_timeout = int(os.getenv('API_TIMEOUT', '30'))
        
        # Repository clone settings
        self.ssh_port = int(os.getenv('SSH_PORT', '22'))
        self.ssh_user = os.getenv('SSH_USER', 'git')
        
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

    def _parse_list(self, value: str) -> List[str]:
        """Parse comma-separated string into list."""
        if not value:
            return []
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def get_ssh_url(self, project_path: str) -> str:
        """Generate SSH URL for a project."""
        if not self.gitlab_url:
            raise ValueError("GitLab URL not configured")
            
        # Extract hostname from GitLab URL
        from urllib.parse import urlparse
        parsed = urlparse(self.gitlab_url)
        hostname = parsed.hostname
        
        if self.ssh_port == 22:
            return f"{self.ssh_user}@{hostname}:{project_path}.git"
        else:
            return f"ssh://{self.ssh_user}@{hostname}:{self.ssh_port}/{project_path}.git"
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        errors = []
        
        if not self.gitlab_url:
            errors.append("GITLAB_URL is required")
        
        if not self.gitlab_token:
            errors.append("GITLAB_TOKEN is required")
        
        if self.default_analysis_days <= 0:
            errors.append("DEFAULT_ANALYSIS_DAYS must be positive")
        
        if self.max_repositories <= 0:
            errors.append("MAX_REPOSITORIES must be positive")
        
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))
        
        return True
    
    def __str__(self):
        """String representation of configuration."""
        return (
            f"GitLabAnalysisConfig(\n"
            f"  gitlab_url={self.gitlab_url}\n"
            f"  default_days={self.default_analysis_days}\n"
            f"  output_dir={self.output_directory}\n"
            f"  max_repos={self.max_repositories}\n"
            f"  ssh_port={self.ssh_port}\n"
            f")"
        )


def load_config() -> GitLabAnalysisConfig:
    """Load and return the configuration instance."""
    return GitLabAnalysisConfig()


def main():
    """Test configuration loading."""
    try:
        config = load_config()
        config.validate()
        print("✅ Configuration loaded successfully!")
        print(config)
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main()) 