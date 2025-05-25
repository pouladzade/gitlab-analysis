#!/usr/bin/env python3

import os
import re
import pandas as pd
import argparse
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import git
from pathlib import Path
import requests
import json
from urllib.parse import urljoin
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LocalGitAnalyzer:
    def __init__(self, gitlab_url=None, private_token=None):
        self.projects_dir = os.path.join(os.getcwd(), 'projects')
        # Support both GITLAB_URL and GITLAB_URL env vars
        self.gitlab_url = gitlab_url or os.getenv('GITLAB_URL', 'https://gitlab.com')
        # Support both GITLAB_PRIVATE_TOKEN and GITLAB_TOKEN env vars
        self.private_token = private_token or os.getenv('GITLAB_PRIVATE_TOKEN') or os.getenv('GITLAB_TOKEN')
        if not self.private_token:
            raise ValueError("GitLab private token is required. Set it via GITLAB_TOKEN or GITLAB_PRIVATE_TOKEN environment variable or --token argument")

    def fetch_recent_repositories(self, days=30, max_repos=50, since_date=None, until_date=None, verbose=False):
        """Fetch recent repositories from GitLab that have at least one commit in the period. Returns (included, skipped) lists."""
        # Always use UTC and print the exact range
        now_utc = datetime.now(timezone.utc)
        if since_date is None:
            since_date = (now_utc - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')
        if until_date is None:
            until_date = now_utc.replace(hour=23, minute=59, second=59, microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')
        print(f"Using since={since_date} and until={until_date} (UTC) for all API calls.")
        
        headers = {
            'PRIVATE-TOKEN': self.private_token
        }
        projects_url = urljoin(self.gitlab_url, '/api/v4/projects')
        params = {
            'simple': 'true',
            'order_by': 'last_activity_at',
            'sort': 'desc',
            'per_page': 100,  # Use max allowed per page
            'page': 1
        }
        included = []
        skipped = []
        total_fetched = 0
        try:
            while True:
                response = requests.get(projects_url, headers=headers, params=params)
                response.raise_for_status()
                projects = response.json()
                if not projects:
                    break
                for project in projects:
                    total_fetched += 1
                    project_name = project.get('name_with_namespace', project.get('name', 'UNKNOWN'))
                    project_id = project.get('id', 'UNKNOWN')
                    print(f"Checking project: {project_name} (ID: {project_id})")
                    found_commit = False
                    # Fetch all branches for this project
                    branches_url = urljoin(self.gitlab_url, f"/api/v4/projects/{project_id}/repository/branches")
                    branches_resp = requests.get(branches_url, headers=headers)
                    if branches_resp.status_code == 200:
                        branches = branches_resp.json()
                        for branch in branches:
                            branch_name = branch['name']
                            commits_url = urljoin(self.gitlab_url, f"/api/v4/projects/{project_id}/repository/commits")
                            commit_params = {
                                'since': since_date,
                                'until': until_date,
                                'per_page': 1,
                                'ref_name': branch_name
                            }
                            commits_resp = requests.get(commits_url, headers=headers, params=commit_params)
                            if commits_resp.status_code == 200:
                                commits = commits_resp.json()
                                print(f"  Branch '{branch_name}': commits found in period: {len(commits)}")
                                if len(commits) > 0:
                                    found_commit = True
                                    if verbose:
                                        print(f"Included: {project_name} (has commits in period on branch '{branch_name}')")
                                    break  # No need to check other branches
                            else:
                                print(f"  Branch '{branch_name}': error fetching commits: {commits_resp.status_code} {commits_resp.text}")
                    else:
                        print(f"  Error fetching branches: {branches_resp.status_code} {branches_resp.text}")
                    if found_commit:
                        included.append(project)
                    else:
                        skipped.append(project)
                        if verbose:
                            print(f"Skipped: {project_name} (no commits in period on any branch)")
                # Check for next page
                next_page = response.headers.get('X-Next-Page')
                if next_page:
                    params['page'] = int(next_page)
                else:
                    break
            print(f"Checked {total_fetched} repositories. Found {len(included)} repositories with commits in the period.")
            return included, skipped
        except requests.exceptions.RequestException as e:
            print(f"Error fetching repositories: {str(e)}")
            return [], []

    def save_repository_index(self, projects, timestamp):
        """Save the list of repositories to an index file."""
        index_dir = os.path.join(os.getcwd(), 'gitlab_reports')
        os.makedirs(index_dir, exist_ok=True)
        index_file = os.path.join(index_dir, f'repository_index_{timestamp}.json')
        
        # Create a simplified version of the project data
        index_data = [{
            'name_with_namespace': p['name_with_namespace'],
            'path': p['path'],
            'ssh_url_to_repo': p['ssh_url_to_repo'],
            'web_url': p['web_url']
        } for p in projects]
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2)
        
        print(f"\nRepository index saved to: {index_file}")
        return index_file

    def load_repository_index(self, index_file):
        """Load repository information from an index file."""
        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def clone_repositories(self, projects):
        """Clone repositories into the projects directory using custom SSH URL format."""
        os.makedirs(self.projects_dir, exist_ok=True)
        
        for project in projects:
            # Get the full path including group structure
            repo_name = project['name_with_namespace'].replace(' / ', '/')
            repo_path = os.path.join(self.projects_dir, repo_name)
            
            # Create group directories if they don't exist
            os.makedirs(os.path.dirname(repo_path), exist_ok=True)
            
            # Convert ssh_url_to_repo to custom format
            # Example: git@gitlab.ptc-telematik.de:customerportal/admin-app.git -> ssh://{user_host}:7999/{path}
            original_ssh_url = project['ssh_url_to_repo']
            if original_ssh_url.startswith('git@'):
                user_host, path = original_ssh_url.split(':', 1)
                custom_ssh_url = f"ssh://{user_host}:7999/{path}"
            else:
                custom_ssh_url = original_ssh_url  # fallback
            
            if os.path.exists(repo_path):
                print(f"Repository {repo_name} exists, force updating...")
                try:
                    repo = git.Repo(repo_path)
                    # Force reset to remote state
                    repo.remotes.origin.fetch()
                    repo.git.reset('--hard', 'origin/main')  # Reset to remote main branch
                    print(f"  ✓ Successfully force updated {repo_name}")
                except Exception as e:
                    print(f"  ⚠️ Warning: Error updating {repo_name}: {str(e)}")
                continue
            
            print(f"Cloning {repo_name} via SSH ({custom_ssh_url})...")
            try:
                git.Repo.clone_from(custom_ssh_url, repo_path)
                print(f"Successfully cloned {repo_name}")
            except Exception as e:
                print(f"Error cloning {repo_name}: {str(e)}")

    def is_merge_commit(self, commit) -> bool:
        """Check if a commit is a merge commit or pull request by examining parents and message."""
        # Check if commit has multiple parents (typical merge)
        if len(commit.parents) > 1:
            return True
        
        # Check commit message for merge patterns
        message = commit.message.lower()
        merge_patterns = [
            r'merge\s+pull\s+request',
            r'merge\s+branch',
            r'merge\s+remote[-\s]tracking\s+branch',
            r'pull\s+request\s+#\d+',
            r'^merge\s+',
            r'merged\s+in\s+',
            r'auto-merge',
            r'automatic\s+merge',
            r'conflicts\s+resolved',
        ]
        
        for pattern in merge_patterns:
            if re.search(pattern, message):
                return True
        
        return False

    def analyze_repository(self, repo_path: str, since_date: str, until_date: str, authors: List[str] = None) -> Dict[str, Dict[str, int]]:
        """Analyze a single repository and return consolidated author statistics by email."""
        try:
            repo = git.Repo(repo_path)
            
            # Convert string dates to datetime objects for git log filtering
            since_dt = datetime.strptime(since_date, '%Y-%m-%d')
            until_dt = datetime.strptime(until_date, '%Y-%m-%d') + timedelta(days=1)  # Include the end date
            
            # Get all commits in the date range, excluding merges
            commits = list(repo.iter_commits(
                since=since_dt,
                until=until_dt,
                all=True  # All branches
            ))
            
            # Filter out merge commits
            regular_commits = [commit for commit in commits if not self.is_merge_commit(commit)]
            
            author_stats = {}
            
            for commit in regular_commits:
                author_email = commit.author.email.lower().strip()
                author_name = commit.author.name.strip()
                commit_date = commit.committed_datetime.date()
                
                # Filter by authors if specified
                if authors:
                    if not any(author.lower() in author_name.lower() or author.lower() in author_email.lower() for author in authors):
                        continue
                
                # Initialize author stats if not seen before
                if author_email not in author_stats:
                    author_stats[author_email] = {
                        'name': author_name,  # Keep the name from the first commit we see
                        'email': author_email,
                        'added': 0,
                        'removed': 0,
                        'commit_count': 0,
                        'active_days': set(),
                        'first_commit': None,
                        'last_commit': None
                    }
                
                # Update commit count and active days
                author_stats[author_email]['commit_count'] += 1
                author_stats[author_email]['active_days'].add(commit_date)
                
                # Update first and last commit dates
                if not author_stats[author_email]['first_commit'] or commit_date < author_stats[author_email]['first_commit']:
                    author_stats[author_email]['first_commit'] = commit_date
                if not author_stats[author_email]['last_commit'] or commit_date > author_stats[author_email]['last_commit']:
                    author_stats[author_email]['last_commit'] = commit_date
                
                try:
                    # Get the diff stats for this commit
                    if commit.parents:  # Not the initial commit
                        diffs = commit.parents[0].diff(commit, create_patch=True)
                        for diff in diffs:
                            if diff.a_path:
                                # Try to decode the diff as text; skip if it fails (likely binary)
                                try:
                                    diff_text = diff.diff.decode('utf-8', errors='strict')
                                except UnicodeDecodeError:
                                    continue  # Skip binary files
                                lines = diff_text.split('\n')
                                for line in lines:
                                    if line.startswith('+') and not line.startswith('+++'):
                                        author_stats[author_email]['added'] += 1
                                    elif line.startswith('-') and not line.startswith('---'):
                                        author_stats[author_email]['removed'] += 1
                except Exception as e:
                    # If we can't get diff stats for this commit, skip it
                    print(f"Warning: Could not get diff stats for commit {commit.hexsha[:8]} in {os.path.basename(repo_path)}: {str(e)}")
                    continue
            
            # Convert active_days sets to counts
            for author_email in author_stats:
                author_stats[author_email]['active_days_count'] = len(author_stats[author_email]['active_days'])
                del author_stats[author_email]['active_days']  # Remove the set as it's not serializable
            
            return author_stats
            
        except Exception as e:
            print(f"Error analyzing repository {repo_path}: {str(e)}")
            return {}

    def analyze_local_repositories(self, repo_paths: List[str], since_date: str = None, until_date: str = None, authors: List[str] = None) -> pd.DataFrame:
        """Analyze multiple local repositories and consolidate results by email."""
        since_date = since_date or (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        until_date = until_date or datetime.now().strftime('%Y-%m-%d')
        
        print(f"Analyzing commits from {since_date} to {until_date}")
        if authors:
            print(f"Filtering by authors: {', '.join(authors)}")
        
        all_stats = {}  # email -> consolidated stats
        
        for repo_path in repo_paths:
            repo_name = os.path.basename(repo_path)
            print(f"Analyzing repository: {repo_name}")
            
            try:
                repo_stats = self.analyze_repository(repo_path, since_date, until_date, authors)
                
                for author_email, stats in repo_stats.items():
                    if author_email not in all_stats:
                        all_stats[author_email] = {
                            'added': 0, 
                            'removed': 0, 
                            'commit_count': 0,
                            'active_days_count': 0,
                            'name': stats['name'], 
                            'email': stats['email'],
                            'first_commit': stats['first_commit'],
                            'last_commit': stats['last_commit'],
                            'total_days': stats['total_days'] if 'total_days' in stats else 0
                        }
                    else:
                        # Update first and last commit dates
                        if stats['first_commit'] and (not all_stats[author_email]['first_commit'] or stats['first_commit'] < all_stats[author_email]['first_commit']):
                            all_stats[author_email]['first_commit'] = stats['first_commit']
                        if stats['last_commit'] and (not all_stats[author_email]['last_commit'] or stats['last_commit'] > all_stats[author_email]['last_commit']):
                            all_stats[author_email]['last_commit'] = stats['last_commit']
                    
                    all_stats[author_email]['added'] += stats['added']
                    all_stats[author_email]['removed'] += stats['removed']
                    all_stats[author_email]['commit_count'] += stats['commit_count']
                    all_stats[author_email]['active_days_count'] += stats['active_days_count']
                    
            except Exception as e:
                print(f"Error analyzing repository {repo_name}: {str(e)}")
                continue
        
        if not all_stats:
            print("\nNo data available to generate report.")
            return pd.DataFrame(columns=['added', 'removed', 'net', 'name', 'email', 'commit_count', 'avg_commits_per_day', 'active_days_count', 'first_commit', 'last_commit'])
        
        # Calculate final averages for each author
        for author_email, stats in all_stats.items():
            if stats['first_commit'] and stats['last_commit']:
                total_days = (stats['last_commit'] - stats['first_commit']).days + 1
                stats['total_days'] = total_days
                stats['avg_commits_per_day'] = stats['commit_count'] / total_days if total_days > 0 else 0
                stats['avg_commits_per_active_day'] = stats['commit_count'] / stats['active_days_count'] if stats['active_days_count'] > 0 else 0
            else:
                stats['total_days'] = 0
                stats['avg_commits_per_day'] = 0
                stats['avg_commits_per_active_day'] = 0
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(all_stats, orient='index')
        df['net'] = df['added'] - df['removed']
        df = df.sort_values('net', ascending=False)
        
        return df

    def save_analysis_report(self, df: pd.DataFrame, since_date: str, until_date: str, analyzed_repos: list = None, skipped_repos: list = None) -> str:
        """Save the analysis report to a file with proper email-based grouping and fixed period formatting, and include a list of analyzed and skipped repositories with reasons."""
        if df.empty and not (analyzed_repos or skipped_repos):
            return None
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        main_dir = os.path.join(os.getcwd(), 'gitlab_reports')
        analysis_dir = os.path.join(main_dir, f'analysis_{timestamp}')
        os.makedirs(analysis_dir, exist_ok=True)
        report_file = os.path.join(analysis_dir, f'analysis_report_enhanced_{timestamp}.txt')
        csv_file = os.path.join(analysis_dir, f'analysis_report_enhanced_{timestamp}.csv')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("Enhanced Git Repository Analysis Report (Email-Consolidated with Commit Frequency)\n")
            f.write("=" * 120 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Analysis Period: {since_date} to {until_date}\n")
            f.write("Scope: All Local Repositories\n")
            f.write("Note: Excluding merge commits and pull requests\n")
            f.write("Note: Authors grouped by email address to consolidate duplicate identities\n")
            f.write("=" * 120 + "\n\n")
            # Repository inclusion summary
            f.write("REPOSITORY INCLUSION SUMMARY:\n")
            f.write("-" * 40 + "\n")
            active_count = len(analyzed_repos) if analyzed_repos else 0
            nonactive_count = len(skipped_repos) if skipped_repos else 0
            total_count = active_count + nonactive_count
            f.write(f"Active repositories (included): {active_count}\n")
            f.write(f"Non-active repositories (skipped): {nonactive_count}\n")
            f.write(f"Total repositories considered: {total_count}\n\n")
            if analyzed_repos:
                for repo in analyzed_repos:
                    f.write(f"Included: {repo['name']} ({repo['web_url']}) - has commits in period\n")
            if skipped_repos:
                for repo in skipped_repos:
                    f.write(f"Skipped: {repo['name_with_namespace']} ({repo['web_url']}) - no commits in period\n")
            f.write("\n")
            # List of analyzed repositories with links
            if analyzed_repos:
                f.write("ANALYZED REPOSITORIES:\n")
                f.write("-" * 40 + "\n")
                for repo in analyzed_repos:
                    f.write(f"- {repo['name']}: {repo['web_url']}\n")
                f.write("\n")
            # Write summary statistics
            f.write("SUMMARY STATISTICS:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Authors: {len(df)}\n")
            f.write(f"Total Lines Added: {df['added'].sum():,}\n")
            f.write(f"Total Lines Removed: {df['removed'].sum():,}\n")
            f.write(f"Net Lines Added: {df['net'].sum():,}\n")
            f.write(f"Total Commits: {df['commit_count'].sum():,}\n")
            f.write(f"Average Commits per Author: {df['commit_count'].mean():.1f}\n")
            f.write("\n")
            
            # Write detailed report
            f.write("DETAILED REPORT BY AUTHOR (CONSOLIDATED BY EMAIL WITH COMMIT FREQUENCY):\n")
            f.write("-" * 120 + "\n")
            f.write(f"{'Author (Email)':<35} | {'Added':>8} | {'Removed':>8} | {'Net':>8} | {'Commits':>7} | {'Avg/Day':>7} | {'Act.Days':>8} | {'Period':>15}\n")
            f.write("-" * 120 + "\n")
            
            for author_email, row in df.iterrows():
                # Format as "Name (email)" for display
                author_display = f"{row['name']} ({author_email})"
                if len(author_display) > 35:
                    author_display = author_display[:32] + "..."
                
                # Format date range with proper year handling
                if row['first_commit'] and row['last_commit']:
                    if row['first_commit'] == row['last_commit']:
                        period = row['first_commit'].strftime('%Y-%m-%d')
                    else:
                        # Check if commits span multiple years
                        if row['first_commit'].year == row['last_commit'].year:
                            # Same year: show MM/DD-MM/DD/YY
                            period = f"{row['first_commit'].strftime('%m/%d')}-{row['last_commit'].strftime('%m/%d/%y')}"
                        else:
                            # Different years: show MM/DD/YY-MM/DD/YY
                            period = f"{row['first_commit'].strftime('%m/%d/%y')}-{row['last_commit'].strftime('%m/%d/%y')}"
                else:
                    period = "N/A"
                
                f.write(f"{author_display:<35} | {row['added']:>8} | {row['removed']:>8} | {row['net']:>8} | {row['commit_count']:>7} | {row['avg_commits_per_day']:>7.2f} | {row['active_days_count']:>8} | {period:>15}\n")
                
            f.write("\n" + "=" * 120 + "\n")
            f.write("Report generated by Enhanced Local Git Analyzer (Email-Consolidated Version)\n")
            f.write("\nColumn Descriptions:\n")
            f.write("- Added: Lines of code added\n")
            f.write("- Removed: Lines of code removed\n")
            f.write("- Net: Net lines added (Added - Removed)\n")
            f.write("- Commits: Total number of commits\n")
            f.write("- Avg/Day: Average commits per day over total period (first to last commit)\n")
            f.write("- Act.Days: Number of unique days with commits\n")
            f.write("- Period: Date range from first to last commit\n")
        
        # Save CSV report if there is data
        if not df.empty:
            df_csv = df.copy()
            df_csv.index.name = 'email'
            df_csv.to_csv(csv_file)
            print(f"\nEnhanced analysis reports saved to: {analysis_dir}")
            print(f"  - Text report: {os.path.basename(report_file)}")
            print(f"  - CSV report: {os.path.basename(csv_file)}")
        else:
            print(f"\nList-only report saved to: {analysis_dir}")
            print(f"  - Text report: {os.path.basename(report_file)}")
        return analysis_dir

def parse_args():
    parser = argparse.ArgumentParser(description='Analyze local Git repositories with email-based author consolidation and commit frequency')
    parser.add_argument('--since', type=str, default=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'), 
                        help='Start date for analysis (YYYY-MM-DD)')
    parser.add_argument('--until', type=str, default=datetime.now().strftime('%Y-%m-%d'),
                        help='End date for analysis (YYYY-MM-DD)')
    parser.add_argument('--authors', type=str, nargs='+', help='Filter by specific authors (names or emails)')
    parser.add_argument('--gitlab-url', type=str, help='GitLab instance URL (default: https://gitlab.com)')
    parser.add_argument('--token', type=str, help='GitLab private token')
    parser.add_argument('--days', type=int, default=365, help='Number of days to look back for recent repositories')
    parser.add_argument('--max-repos', type=int, default=50, help='Maximum number of repositories to fetch')
    parser.add_argument('--mode', type=str, choices=['online', 'offline'], default='online', help='Analysis mode: online (fetch & clone) or offline (analyze local only)')
    parser.add_argument('--verbose', action='store_true', help='Show which repositories were included or skipped and why')
    parser.add_argument('--list-only', action='store_true', help='Only list included/skipped repositories, print and generate report, do not clone or analyze')
    return parser.parse_args()

def main():
    print("Enhanced Local Git Repository Analyzer (Email-Consolidated with Commit Frequency)")
    print("=" * 100)
    
    args = parse_args()
    
    try:
        analyzer = LocalGitAnalyzer(args.gitlab_url, args.token)
        
        if args.list_only:
            included, skipped = analyzer.fetch_recent_repositories(args.days, args.max_repos, args.since + 'T00:00:00Z', args.until + 'T23:59:59Z', verbose=args.verbose)
            analyzed_repos = [{'name': p['name_with_namespace'], 'web_url': p['web_url']} for p in included]
            skipped_repos = skipped
            # Print summary to command line
            print("\nREPOSITORY INCLUSION SUMMARY:")
            print("-" * 40)
            for repo in analyzed_repos:
                print(f"Included: {repo['name']} ({repo['web_url']}) - has commits in period")
            for repo in skipped_repos:
                print(f"Skipped: {repo['name_with_namespace']} ({repo['web_url']}) - no commits in period")
            # Generate report file (empty DataFrame for stats)
            import pandas as pd
            df_empty = pd.DataFrame()
            output_dir = analyzer.save_analysis_report(df_empty, args.since, args.until, analyzed_repos, skipped_repos)
            print(f"\nList-only report saved to: {output_dir}")
            return
        
        if args.mode == 'online':
            included, skipped = analyzer.fetch_recent_repositories(args.days, args.max_repos, args.since + 'T00:00:00Z', args.until + 'T23:59:59Z', verbose=args.verbose)
            if included:
                # Save repository index
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                index_file = analyzer.save_repository_index(included, timestamp)
                print(f"\nSaved repository index to: {index_file}")
                print("You can use this index file for offline analysis later")
                
                # Clone repositories
                analyzer.clone_repositories(included)
                analyzed_repos = [{'name': p['name_with_namespace'], 'web_url': p['web_url']} for p in included]
            else:
                print("No recent repositories found or failed to fetch from GitLab.")
                analyzed_repos = []
            skipped_repos = skipped
        else:
            print("Running in OFFLINE mode: Only analyzing already-downloaded repositories.")
            analyzed_repos = []
            skipped_repos = []
        
        # Find all cloned repositories in the projects directory
        repo_paths = []
        projects_dir = analyzer.projects_dir
        if os.path.exists(projects_dir):
            for root, dirs, files in os.walk(projects_dir):
                if '.git' in dirs:
                    repo_paths.append(root)
        
        if not repo_paths:
            print(f"No Git repositories found in {projects_dir}")
            return
        
        print(f"Found {len(repo_paths)} repositories to analyze")
        
        # Analyze the repositories
        df = analyzer.analyze_local_repositories(repo_paths, args.since, args.until, args.authors)
        
        # In offline mode, add repositories to analyzed_repos if they have commits
        if args.mode == 'offline' and not df.empty:
            for repo_path in repo_paths:
                repo_name = os.path.basename(repo_path)
                try:
                    repo = git.Repo(repo_path)
                    commits = list(repo.iter_commits(since=args.since, until=args.until))
                    if commits:
                        analyzed_repos.append({
                            'name': repo_name,
                            'web_url': f"file://{os.path.abspath(repo_path)}"
                        })
                    else:
                        skipped_repos.append({
                            'name_with_namespace': repo_name,
                            'web_url': f"file://{os.path.abspath(repo_path)}"
                        })
                except Exception as e:
                    print(f"Error checking repository {repo_name}: {str(e)}")
                    skipped_repos.append({
                        'name_with_namespace': repo_name,
                        'web_url': f"file://{os.path.abspath(repo_path)}"
                    })
        
        if not df.empty:
            # Save report
            output_dir = analyzer.save_analysis_report(df, args.since, args.until, analyzed_repos, skipped_repos)
            
            # Also print summary to console
            print(f"\nAnalysis Period: {args.since} to {args.until}")
            print("\nENHANCED CONSOLIDATED SUMMARY (Email-Grouped with Commit Frequency):")
            print("-" * 120)
            print(f"{'Author (Email)':<35} | {'Added':>8} | {'Removed':>8} | {'Net':>8} | {'Commits':>7} | {'Avg/Day':>7} | {'Act.Days':>8} | {'Period':>15}")
            print("-" * 120)
            
            for author_email, row in df.iterrows():
                author_display = f"{row['name']} ({author_email})"
                if len(author_display) > 35:
                    author_display = author_display[:32] + "..."
                
                # Format date range with proper year handling
                if row['first_commit'] and row['last_commit']:
                    if row['first_commit'] == row['last_commit']:
                        period = row['first_commit'].strftime('%Y-%m-%d')
                    else:
                        # Check if commits span multiple years
                        if row['first_commit'].year == row['last_commit'].year:
                            # Same year: show MM/DD-MM/DD/YY
                            period = f"{row['first_commit'].strftime('%m/%d')}-{row['last_commit'].strftime('%m/%d/%y')}"
                        else:
                            # Different years: show MM/DD/YY-MM/DD/YY
                            period = f"{row['first_commit'].strftime('%m/%d/%y')}-{row['last_commit'].strftime('%m/%d/%y')}"
                else:
                    period = "N/A"
                
                print(f"{author_display:<35} | {row['added']:>8} | {row['removed']:>8} | {row['net']:>8} | {row['commit_count']:>7} | {row['avg_commits_per_day']:>7.2f} | {row['active_days_count']:>8} | {period:>15}")
                
            print("\nSUMMARY STATISTICS:")
            print(f"Total Authors: {len(df)}")
            print(f"Total Lines Added: {df['added'].sum():,}")
            print(f"Total Lines Removed: {df['removed'].sum():,}")
            print(f"Net Lines Added: {df['net'].sum():,}")
            print(f"Total Commits: {df['commit_count'].sum():,}")
            print(f"Average Commits per Author: {df['commit_count'].mean():.1f}")
            
        else:
            print("No analysis data generated.")
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("\nPlease set your GitLab private token using one of these methods:")
        print("1. Set the GITLAB_TOKEN or GITLAB_PRIVATE_TOKEN environment variable")
        print("2. Use the --token command line argument")
        print("\nYou can create a private token in GitLab under Settings > Access Tokens")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 