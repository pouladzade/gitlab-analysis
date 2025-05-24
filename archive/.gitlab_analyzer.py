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

# Load environment variables
load_dotenv()

class GitLabAnalyzer:
    def __init__(self, gitlab_url: str, private_token: str):
        self.gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
        self.gl.auth()

    def get_all_repositories(self) -> List[Dict]:
        """Get all repositories from GitLab instance."""
        projects = self.gl.projects.list(all=True)
        return [{'id': p.id, 'name': p.name, 'path': p.path_with_namespace} for p in projects]

    def analyze_repository(self, repo_path: str, since_date: str, until_date: str) -> Dict[str, Dict[str, int]]:
        """Analyze a single repository and return author statistics."""
        repo = git.Repo(repo_path)

        # Get all commits in the date range
        commits = list(repo.iter_commits(since=since_date, until=until_date))

        # Initialize statistics dictionary
        stats = {}

        for commit in commits:
            if len(commit.parents) > 1:  # Skip merge commits
                continue

            author = commit.author.name
            if author not in stats:
                stats[author] = {'added': 0, 'removed': 0}

            # Get diff stats
            if commit.parents:
                diff = commit.parents[0].diff(commit)
                for d in diff:
                    if d.a_blob and d.b_blob:
                        stats[author]['added'] += d.stats.get('insertions', 0)
                        stats[author]['removed'] += d.stats.get('deletions', 0)

        return stats

    def generate_report(self, since_date: str = None, until_date: str = None) -> pd.DataFrame:
        """Generate a report for all repositories."""
        if since_date is None:
            since_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if until_date is None:
            until_date = datetime.now().strftime('%Y-%m-%d')

        all_stats = {}
        repos = self.get_all_repositories()

        with tempfile.TemporaryDirectory() as temp_dir:
            for repo in repos:
                print(f"Analyzing repository: {repo['path']}")

                # Clone repository
                repo_path = os.path.join(temp_dir, repo['path'].replace('/', '_'))
                git.Repo.clone_from(f"{self.gl.url}/{repo['path']}.git", repo_path)

                # Analyze repository
                repo_stats = self.analyze_repository(repo_path, since_date, until_date)

                # Accumulate stats
                for author, stats in repo_stats.items():
                    if author not in all_stats:
                        all_stats[author] = {'added': 0, 'removed': 0}
                    all_stats[author]['added'] += stats['added']
                    all_stats[author]['removed'] += stats['removed']

        # Convert to DataFrame
        df = pd.DataFrame.from_dict(all_stats, orient='index')
        df['net'] = df['added'] - df['removed']
        df = df.sort_values('net', ascending=False)

        return df

def main():
    # Get GitLab credentials from environment variables
    gitlab_url = os.getenv('GITLAB_URL')
    private_token = os.getenv('GITLAB_PRIVATE_TOKEN')

    if not gitlab_url or not private_token:
        print("Please set GITLAB_URL and GITLAB_PRIVATE_TOKEN environment variables")
        return

    analyzer = GitLabAnalyzer(gitlab_url, private_token)

    # Generate report for the last year
    since_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    until_date = datetime.now().strftime('%Y-%m-%d')

    print(f"\nGenerating report from {since_date} to {until_date}")
    print("=" * 80)

    df = analyzer.generate_report(since_date, until_date)

    # Print report
    print("\nCumulative Lines Added/Removed Report Across All Repositories")
    print("-" * 80)
    print(f"{'Author':<30} | {'Added':>10} | {'Removed':>10} | {'Net':>10}")
    print("-" * 80)

    for author, row in df.iterrows():
        print(f"{author:<30} | {row['added']:>10} | {row['removed']:>10} | {row['net']:>10}")

if __name__ == "__main__":
    main()
