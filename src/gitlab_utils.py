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

# Load environment variables from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)


class GitLabConfig:
    """Configuration class for GitLab settings."""
    
    def __init__(self):
        """Initialize GitLab configuration from environment variables."""
        self.gitlab_url = os.getenv('GITLAB_URL')
        self.gitlab_token = os.getenv('GITLAB_PRIVATE_TOKEN') or os.getenv('GITLAB_TOKEN')
        
        if not self.gitlab_url:
            raise ValueError("GITLAB_URL environment variable is required. Please set it in your .env file.")
        
        if not self.gitlab_token:
            raise ValueError("GITLAB_TOKEN environment variable is required. Please set it in your .env file.")
    
    def __str__(self):
        return f"GitLabConfig(url={self.gitlab_url}, token_set={bool(self.gitlab_token)})"


class GitLabClient:
    """GitLab API client wrapper."""
    
    def __init__(self, config: Optional[GitLabConfig] = None):
        """Initialize GitLab client with configuration."""
        self.config = config or GitLabConfig()
        
        try:
            self.gl = gitlab.Gitlab(self.config.gitlab_url, private_token=self.config.gitlab_token)
            self.gl.auth()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to GitLab at {self.config.gitlab_url}: {str(e)}")
    
    def get_project(self, project_id_or_path: str):
        """Get a GitLab project by ID or path."""
        try:
            return self.gl.projects.get(project_id_or_path)
        except gitlab.exceptions.GitlabGetError as e:
            raise ValueError(f"Project '{project_id_or_path}' not found or not accessible: {str(e)}")
    
    def list_projects(self, **kwargs):
        """List GitLab projects with optional filters."""
        return self.gl.projects.list(all=True, **kwargs)


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


def create_timestamped_directory(base_path: str, prefix: str = "") -> str:
    """Create a timestamped directory for outputs."""
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dir_name = f"{prefix}_{timestamp}" if prefix else timestamp
    full_path = os.path.join(base_path, dir_name)
    
    os.makedirs(full_path, exist_ok=True)
    return full_path 