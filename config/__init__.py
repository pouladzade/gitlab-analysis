"""
GitLab Analysis Tool - Configuration Package

This package provides configuration management for the GitLab analysis tools.
"""

from .settings import GitLabAnalysisConfig, load_config

__all__ = ['GitLabAnalysisConfig', 'load_config'] 