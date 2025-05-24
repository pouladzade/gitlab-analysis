#!/usr/bin/env python3

import os
import gitlab
import git
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import tempfile
import shutil
from typing import Dict, List, Tuple
import argparse
import json
from pathlib import Path

# Load environment variables
load_dotenv()

class GitLabAnalyzer:
    def __init__(self, gitlab_url: str = None, private_token: str = None):
        # Use the provided URL or default to PTC Telematik GitLab
        self.ssh_url = gitlab_url or 'git@gitlab.ptc-telematik.de'
        # For API access, we need the HTTPS URL
        self.api_url = 'https://gitlab.ptc-telematik.de'
        self.ssh_key_path = os.path.expanduser('~/.ssh/id_ed25519')
        
        if not os.path.exists(self.ssh_key_path):
            raise FileNotFoundError(f"SSH key not found at {self.ssh_key_path}")
            
        try:
            # Initialize GitLab API client with HTTPS URL
            self.gl = gitlab.Gitlab(self.api_url, private_token=private_token)
            # Only authenticate, no write operations
            self.gl.auth()
            print(f"Successfully connected to GitLab instance: {self.api_url}")
        except Exception as e:
            print(f"Error connecting to GitLab instance {self.api_url}: {str(e)}")
            print("Please ensure:")
            print("1. The GitLab URL is correct")
            print("2. You have network access to the GitLab instance")
            print("3. Your SSH key is properly configured")
            print("4. You have a valid personal access token with read_api scope")
            raise
            
        self.projects_dir = os.path.join(os.getcwd(), 'projects')
        os.makedirs(self.projects_dir, exist_ok=True)
        
    def get_active_repositories(self, since_date: str) -> List[Dict]:
        """Get active repositories from GitLab instance that have commits since the given date."""
        try:
            projects = self.gl.projects.list(all=True)
            active_repos = []
            
            print("\nChecking repository activity in PTC Telematik GitLab (read-only)...")
            for project in projects:
                try:
                    # Fetch the full project object to access all attributes
                    full_project = self.gl.projects.get(project.id)
                    commits = full_project.commits.list(since=since_date, per_page=1)
                    if commits:
                        active_repos.append({
                            'id': full_project.id,
                            'name': full_project.name,
                            'path': full_project.path_with_namespace,
                            'last_commit': commits[0].created_at,
                            'web_url': full_project.web_url
                        })
                        print(f"  Active: {full_project.path_with_namespace} (Last commit: {commits[0].created_at})")
                    else:
                        print(f"  Inactive: {full_project.path_with_namespace} (No commits since {since_date})")
                except Exception as e:
                    print(f"  Error checking {project.path_with_namespace}: {str(e)}")
                    continue
                    
            return active_repos
        except Exception as e:
            print(f"Error accessing GitLab instance: {str(e)}")
            print("Please ensure you have read access to the repositories")
            return []
    
    def save_repository_list(self, repos: List[Dict]):
        """Save the list of active repositories to a text file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        list_file = os.path.join(self.projects_dir, f'ptc_telematik_repositories_{timestamp}.txt')
        
        with open(list_file, 'w', encoding='utf-8') as f:
            f.write("PTC Telematik GitLab Active Repositories (Read-Only Analysis)\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"GitLab Instance: https://gitlab.ptc-telematik.de\n")
            f.write(f"Analysis Type: Read-Only\n\n")
            
            for repo in repos:
                f.write(f"Repository: {repo['path']}\n")
                f.write(f"Last Commit: {repo['last_commit']}\n")
                f.write(f"Web URL: {repo['web_url']}\n")
                f.write("-" * 50 + "\n")
        
        print(f"\nRepository list saved to: {list_file}")
        return list_file

    def clone_repositories(self, repos: List[Dict]) -> List[str]:
        """Clone repositories and return list of successfully cloned paths."""
        successful_clones = []
        failed_clones = []
        
        for repo in repos:
            print(f"\nCloning repository: {repo['path']}")
            
            try:
                # Create proper folder structure for the repository
                # Handle paths with multiple components (e.g., customerportal/maintenance/maintenance)
                path_parts = repo['path'].split('/')
                if len(path_parts) < 2:
                    print(f"  Invalid repository path format: {repo['path']}")
                    failed_clones.append((repo['path'], "Invalid path format"))
                    continue
                
                # Use the first part as namespace, join the rest as project name
                namespace = path_parts[0]
                project = '/'.join(path_parts[1:]) if len(path_parts) > 2 else path_parts[1]
                
                # Create namespace directory if it doesn't exist
                namespace_dir = os.path.join(self.projects_dir, namespace)
                os.makedirs(namespace_dir, exist_ok=True)
                
                # Full path for the repository (flatten nested paths for filesystem)
                safe_project_name = project.replace('/', '_')
                repo_path = os.path.join(namespace_dir, safe_project_name)
                
                # Check if repository already exists
                if os.path.exists(repo_path):
                    if os.path.exists(os.path.join(repo_path, '.git')):
                        print(f"  Repository already exists, skipping clone: {repo['path']}")
                        successful_clones.append(repo_path)
                        continue
                    else:
                        print(f"  Directory exists but is not a git repository, removing: {repo['path']}")
                        shutil.rmtree(repo_path)
                
                print(f"  Cloning repository (read-only): {repo['path']}")
                # Use correct SSH URL format with port 7999
                clone_url = f"ssh://git@gitlab.ptc-telematik.de:7999/{repo['path']}.git"
                print(f"  Using clone URL: {clone_url}")
                git.Repo.clone_from(clone_url, repo_path)
                
                # Verify the clone was successful
                if os.path.exists(os.path.join(repo_path, '.git')):
                    successful_clones.append(repo_path)
                    print(f"  Successfully cloned: {repo['path']}")
                else:
                    raise Exception("Repository was not cloned successfully")
                    
            except Exception as e:
                error_msg = f"Error cloning repository {repo['path']}: {str(e)}"
                print(error_msg)
                failed_clones.append((repo['path'], str(e)))
                continue
        
        # Print summary
        print("\nCloning Summary:")
        print(f"Successfully cloned: {len(successful_clones)} repositories")
        if failed_clones:
            print(f"Failed to clone: {len(failed_clones)} repositories")
            print("\nFailed repositories:")
            for repo_path, error in failed_clones:
                print(f"  - {repo_path}: {error}")
        
        return successful_clones
    
    def is_merge_commit(self, commit) -> bool:
        """Check if a commit is a merge commit or pull request merge."""
        # Check for merge commit
        if len(commit.parents) > 1:
            return True
            
        # Check commit message for common merge patterns
        merge_patterns = [
            'merge',
            'merged',
            'pull request',
            'pull-request',
            'pr #',
            'merge branch',
            'merge pull request'
        ]
        
        commit_msg = commit.message.lower()
        return any(pattern in commit_msg for pattern in merge_patterns)

    def analyze_repository(self, repo_path: str, since_date: str, until_date: str, authors: List[str] = None) -> Dict[str, Dict[str, int]]:
        """Analyze a single repository and return author statistics."""
        repo = git.Repo(repo_path)
        
        # Get all commits in the date range (read-only)
        commits = list(repo.iter_commits(since=since_date, until=until_date))
        
        # Initialize statistics dictionary and email mapping
        stats = {}
        email_to_name = {}  # Track email -> preferred name mapping
        
        for commit in commits:
            # Skip merge commits and pull request merges
            if self.is_merge_commit(commit):
                continue
                
            author_name = commit.author.name
            author_email = commit.author.email
            
            # Use email as the primary identifier to group authors
            author_key = author_email
            
            if authors and author_name not in authors and author_email not in authors:  # Skip if author not in specified list
                continue
                
            if author_key not in stats:
                stats[author_key] = {'added': 0, 'removed': 0}
                # Store the most common name for this email (first occurrence for now)
                email_to_name[author_key] = author_name
            
            if commit.parents:
                # Use commit.stats to get total insertions/deletions
                file_stats = commit.stats.files
                for file_path, file_stat in file_stats.items():
                    if file_path.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.go', '.rb', '.php', '.swift', '.kt', '.rs')):
                        stats[author_key]['added'] += file_stat.get('insertions', 0)
                        stats[author_key]['removed'] += file_stat.get('deletions', 0)
        
        # Return stats with email-to-name mapping included
        for email, author_stats in stats.items():
            author_stats['name'] = email_to_name[email]
            author_stats['email'] = email
        
        return stats
    
    def analyze_local_repositories(self, repo_paths: List[str], since_date: str = None, until_date: str = None, authors: List[str] = None) -> pd.DataFrame:
        """Analyze already cloned repositories offline."""
        if since_date is None:
            since_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if until_date is None:
            until_date = datetime.now().strftime('%Y-%m-%d')
            
        all_stats = {}
        
        print(f"\nAnalyzing {len(repo_paths)} local repositories...")
        
        for repo_path in repo_paths:
            repo_name = os.path.basename(repo_path)
            print(f"\nAnalyzing repository: {repo_name}")
            
            try:
                # Analyze repository (read-only)
                repo_stats = self.analyze_repository(repo_path, since_date, until_date, authors)
                
                # Accumulate stats (now using email as key)
                for author_email, stats in repo_stats.items():
                    if author_email not in all_stats:
                        all_stats[author_email] = {
                            'added': 0, 
                            'removed': 0, 
                            'name': stats['name'], 
                            'email': stats['email']
                        }
                    all_stats[author_email]['added'] += stats['added']
                    all_stats[author_email]['removed'] += stats['removed']
            except Exception as e:
                print(f"Error analyzing repository {repo_name}: {str(e)}")
                continue
        
        if not all_stats:
            print("\nNo data available to generate report.")
            return pd.DataFrame(columns=['added', 'removed', 'net', 'name', 'email'])
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(all_stats, orient='index')
        df['net'] = df['added'] - df['removed']
        df = df.sort_values('net', ascending=False)
        
        return df

    def get_apps_repositories(self, since_date: str) -> List[Dict]:
        """Get active repositories from the Apps group that have commits since the given date."""
        try:
            active_repos = []
            print("\nSearching for Apps group and its projects...")
            
            # First try to get the group directly by path
            try:
                apps_group = self.gl.groups.get('customerportal')
                print(f"Found Apps group: {apps_group.name} (path: {apps_group.path})")
            except Exception as e:
                print(f"Could not find Apps group by path 'customerportal': {str(e)}")
                apps_group = None
            
            # If we couldn't get the group by path, try to find it by searching all groups
            if not apps_group:
                print("Searching for customerportal group in all groups...")
                groups = self.gl.groups.list(all=True)
                for group in groups:
                    if group.name.lower() == 'apps' or group.path.lower() == 'customerportal':
                        apps_group = group
                        print(f"Found Apps group by search: {group.name} (path: {group.path})")
                        break
            
            # If we still don't have the group, try to find projects directly
            if not apps_group:
                print("Could not find Apps group directly. Searching for customerportal projects...")
                projects = self.gl.projects.list(all=True)
                for project in projects:
                    if project.path_with_namespace.startswith('customerportal/'):
                        try:
                            # Fetch the full project object to access commits
                            full_project = self.gl.projects.get(project.id)
                            commits = full_project.commits.list(since=since_date, per_page=1)
                            if commits:
                                active_repos.append({
                                    'id': full_project.id,
                                    'name': full_project.name,
                                    'path': full_project.path_with_namespace,
                                    'last_commit': commits[0].created_at,
                                    'web_url': full_project.web_url
                                })
                                print(f"  Active: {full_project.path_with_namespace} (Last commit: {commits[0].created_at})")
                            else:
                                print(f"  Inactive: {full_project.path_with_namespace} (No commits since {since_date})")
                        except Exception as e:
                            print(f"  Error checking {project.path_with_namespace}: {str(e)}")
                            continue
            else:
                # We found the group, now get its projects
                print(f"\nChecking repository activity in {apps_group.name} group (read-only)...")
                projects = apps_group.projects.list(all=True, include_subgroups=True)
                
                for project in projects:
                    try:
                        # Fetch the full project object to access commits
                        full_project = self.gl.projects.get(project.id)
                        commits = full_project.commits.list(since=since_date, per_page=1)
                        if commits:
                            active_repos.append({
                                'id': full_project.id,
                                'name': full_project.name,
                                'path': full_project.path_with_namespace,
                                'last_commit': commits[0].created_at,
                                'web_url': full_project.web_url
                            })
                            print(f"  Active: {full_project.path_with_namespace} (Last commit: {commits[0].created_at})")
                        else:
                            print(f"  Inactive: {full_project.path_with_namespace} (No commits since {since_date})")
                    except Exception as e:
                        print(f"  Error checking {project.path_with_namespace}: {str(e)}")
                        continue
            
            print(f"\nFound {len(active_repos)} active repositories in the Apps group.")
            return active_repos
            
        except Exception as e:
            print(f"Error accessing Apps group: {str(e)}")
            print("Please ensure you have read access to the Apps group")
            return []

    def save_analysis_report(self, df: pd.DataFrame, args) -> str:
        """Save the analysis report to a file."""
        if df.empty:
            return None
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(self.projects_dir, f'ptc_telematik_analysis_report_{timestamp}.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("PTC Telematik GitLab - Lines Added/Removed Report (Read-Only Analysis)\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"GitLab Instance: https://gitlab.ptc-telematik.de\n")
            f.write(f"Analysis Period: {args.since} to {args.until}\n")
            if args.authors:
                f.write(f"Filtered Authors: {', '.join(args.authors)}\n")
            if args.apps_only:
                f.write("Scope: Apps Group Only\n")
            else:
                f.write("Scope: All Accessible Repositories\n")
            f.write("Note: Excluding merge commits and pull requests\n")
            f.write("=" * 80 + "\n\n")
            
            # Write summary statistics
            f.write("SUMMARY STATISTICS:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Authors: {len(df)}\n")
            f.write(f"Total Lines Added: {df['added'].sum():,}\n")
            f.write(f"Total Lines Removed: {df['removed'].sum():,}\n")
            f.write(f"Net Lines Added: {df['net'].sum():,}\n")
            f.write("\n")
            
                        # Write detailed report            f.write("DETAILED REPORT BY AUTHOR:\n")            f.write("-" * 100 + "\n")            f.write(f"{'Author (Email)':<50} | {'Added':>10} | {'Removed':>10} | {'Net':>10}\n")            f.write("-" * 100 + "\n")                        for author_email, row in df.iterrows():                # Format as "Name (email)" for display                author_display = f"{row['name']} ({author_email})"                f.write(f"{author_display:<50} | {row['added']:>10} | {row['removed']:>10} | {row['net']:>10}\n")
                
            f.write("\n" + "=" * 80 + "\n")
            f.write("Report generated by GitLab Analyzer\n")
        
        print(f"\nAnalysis report saved to: {report_file}")
        return report_file

    def save_analysis_report_csv(self, df: pd.DataFrame, args) -> str:
        """Save the analysis report as CSV file."""
        if df.empty:
            return None
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = os.path.join(self.projects_dir, f'ptc_telematik_analysis_report_{timestamp}.csv')
        
        # Add metadata as a comment at the top
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(f"# PTC Telematik GitLab Analysis Report\n")
            f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Analysis Period: {args.since} to {args.until}\n")
            if args.authors:
                f.write(f"# Filtered Authors: {', '.join(args.authors)}\n")
            f.write(f"# Scope: {'Apps Group Only' if args.apps_only else 'All Accessible Repositories'}\n")
            f.write(f"# Note: Excluding merge commits and pull requests\n")
            f.write(f"#\n")
        
        # Append the DataFrame
        df.to_csv(csv_file, mode='a', index_label='Author')
        
        print(f"Analysis report (CSV) saved to: {csv_file}")
        return csv_file

def parse_args():
    parser = argparse.ArgumentParser(description='Generate PTC Telematik GitLab repository analysis report (Read-Only)')
    parser.add_argument('--since', help='Start date (YYYY-MM-DD)',
                       default=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
    parser.add_argument('--until', help='End date (YYYY-MM-DD)',
                       default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument('--authors', nargs='+', help='List of authors to include in the report')
    parser.add_argument('--offline', action='store_true', help='Run analysis on already cloned repositories')
    parser.add_argument('--list-groups', action='store_true', help='List all groups and projects visible to the API user')
    parser.add_argument('--list-all-projects', action='store_true', help='List all projects visible to the API user')
    parser.add_argument('--apps-only', action='store_true', help='Only analyze repositories from the Apps group')
    parser.add_argument('--format', choices=['text', 'csv', 'both'], default='text', help='Output format for the report (default: text)')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Get GitLab URL and token from environment variables or use defaults
    gitlab_url = os.getenv('GITLAB_URL', 'git@gitlab.ptc-telematik.de')
    private_token = os.getenv('GITLAB_TOKEN')
    
    if not private_token and not args.offline:
        print("Error: GITLAB_TOKEN environment variable is not set")
        print("Please set your GitLab personal access token in the .env file:")
        print("GITLAB_TOKEN=your_personal_access_token")
        return
    
    try:
        analyzer = GitLabAnalyzer(gitlab_url, private_token)
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        print("Please ensure your SSH key is properly set up in ~/.ssh/")
        return
    except Exception as e:
        print(f"Error initializing GitLab analyzer: {str(e)}")
        return

    if args.list_groups:
        list_all_groups_and_projects(analyzer)
        return

    if args.list_all_projects:
        list_all_projects(analyzer)
        return

    if args.offline:
        # Get list of repositories in projects directory
        repo_paths = []
        try:
            if not os.path.exists(analyzer.projects_dir):
                print(f"\nProjects directory does not exist: {analyzer.projects_dir}")
                return
                
            for namespace in os.listdir(analyzer.projects_dir):
                namespace_path = os.path.join(analyzer.projects_dir, namespace)
                if os.path.isdir(namespace_path):
                    for project in os.listdir(namespace_path):
                        project_path = os.path.join(namespace_path, project)
                        if os.path.isdir(project_path) and os.path.exists(os.path.join(project_path, '.git')):
                            repo_paths.append(project_path)
        except Exception as e:
            print(f"\nError scanning projects directory: {str(e)}")
            return
        
        if not repo_paths:
            print("\nNo repositories found in projects directory.")
            print(f"Searched in: {analyzer.projects_dir}")
            return
            
        print(f"\nFound {len(repo_paths)} repositories for offline analysis:")
        for repo_path in repo_paths:
            print(f"  - {os.path.relpath(repo_path, analyzer.projects_dir)}")
            
        df = analyzer.analyze_local_repositories(repo_paths, args.since, args.until, args.authors)
    else:
        print(f"\nGenerating read-only report from {args.since} to {args.until}")
        print("=" * 80)
        
        # Get active repositories
        if args.apps_only:
            repos = analyzer.get_apps_repositories(args.since)
        else:
            repos = analyzer.get_active_repositories(args.since)
        if not repos:
            print("\nNo active repositories found in the specified date range.")
            return
            
        # Save repository list
        list_file = analyzer.save_repository_list(repos)
        
        # Clone repositories
        repo_paths = analyzer.clone_repositories(repos)
        if not repo_paths:
            print("\nNo repositories were successfully cloned.")
            return
            
        # Analyze repositories
        df = analyzer.analyze_local_repositories(repo_paths, args.since, args.until, args.authors)
    
    if df.empty:
        print("\nNo data available to generate report.")
        return
    
    # Save analysis report in requested format(s)
    if args.format in ['text', 'both']:
        report_file = analyzer.save_analysis_report(df, args)
    if args.format in ['csv', 'both']:
        csv_file = analyzer.save_analysis_report_csv(df, args)
    
    # Also print summary to console
    print("\nPTC Telematik GitLab - Lines Added/Removed Report (Read-Only Analysis)")
    print("(Excluding merge commits and pull requests)")
    print("-" * 80)
    print(f"{'Author':<30} | {'Added':>10} | {'Removed':>10} | {'Net':>10}")
    print("-" * 80)
    
    for author, row in df.iterrows():
        print(f"{author:<30} | {row['added']:>10} | {row['removed']:>10} | {row['net']:>10}")

def list_all_groups_and_projects(analyzer):
    print("\nListing all groups and their projects visible to the API user:\n" + ("=" * 80))
    try:
        groups = analyzer.gl.groups.list(iterator=True)
        for group in groups:
            print(f"Group: {group.full_path}")
            try:
                projects = group.projects.list(iterator=True)
                for project in projects:
                    print(f"  - {project.path_with_namespace}")
            except Exception as e:
                print(f"  Error listing projects for group {group.full_path}: {e}")
            print()
    except Exception as e:
        print(f"Error listing groups: {e}")

def list_all_projects(analyzer):
    print("\nListing all projects visible to the API user:\n" + ("=" * 80))
    try:
        for project in analyzer.gl.projects.list(iterator=True):
            print(f"{project.path_with_namespace}")
    except Exception as e:
        print(f"Error listing projects: {e}")

def list_apps_group_projects(analyzer):
    print("\nListing all projects in the 'Apps' group:\n" + ("=" * 80))
    try:
        group = analyzer.gl.groups.get('customerportal')
        for project in group.projects.list(iterator=True, include_subgroups=True):
            print(f"{project.path_with_namespace}")
    except Exception as e:
        print(f"Error listing Apps group projects: {e}")

if __name__ == "__main__":
    main()
