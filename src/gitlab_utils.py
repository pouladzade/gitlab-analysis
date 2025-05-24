#!/usr/bin/env python3
"""
GitLab Utilities

Common utilities and helper functions for GitLab API interactions
and repository management.
"""

import os
import gitlab
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GitLabConfig:
    """Configuration management for GitLab connections."""
    
    def __init__(self):
        self.gitlab_url = os.getenv('GITLAB_URL', 'https://gitlab.ptc-telematik.de')
        self.private_token = os.getenv('GITLAB_TOKEN')
        
        if not self.private_token:
            raise ValueError(
                "GitLab private token not found. Set GITLAB_TOKEN environment variable.\n"
                "You can generate a personal access token in GitLab:\n"
                "  Profile → Access Tokens → Personal Access Tokens\n"
                "  Required scopes: api, read_repository"
            )


class GitLabClient:
    """GitLab API client wrapper with common functionality."""
    
    def __init__(self, config: Optional[GitLabConfig] = None):
        if config is None:
            config = GitLabConfig()
        
        self.config = config
        self.gl = gitlab.Gitlab(config.gitlab_url, private_token=config.private_token)
        self.gl.auth()
        print(f"Successfully connected to GitLab instance: {config.gitlab_url}")
    
    def get_project(self, project_path: str):
        """Get a GitLab project by its path."""
        try:
            return self.gl.projects.get(project_path)
        except gitlab.exceptions.GitlabGetError:
            print(f"Could not access GitLab project: {project_path}")
            return None
    
    def format_user_info(self, user_dict: Dict) -> str:
        """Format user information with name and email."""
        if not user_dict:
            return "Unknown"
        
        name = user_dict.get('name', user_dict.get('username', 'Unknown'))
        email = user_dict.get('email', '')
        
        if email:
            return f"{name} ({email})"
        else:
            return name


def create_safe_filename(name: str) -> str:
    """Create a safe filename from a project name."""
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    return safe_name.replace(' ', '_')


def get_projects_directory() -> str:
    """Get the projects directory path."""
    return os.path.join(os.getcwd(), 'projects')


def get_reports_directory() -> str:
    """Get the reports directory path."""
    return os.path.join(os.getcwd(), 'gitlab_reports')


def create_timestamped_directory(report_type: str) -> str:
    """Create a timestamped directory for reports."""
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    main_dir = get_reports_directory()
    output_dir = os.path.join(main_dir, f'{report_type}_{timestamp}')
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir 