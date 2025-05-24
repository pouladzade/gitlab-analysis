#!/usr/bin/env python3

import os
import re
import pandas as pd
import argparse
from datetime import datetime, timedelta
from typing import Dict, List
import git
from pathlib import Path

class LocalGitAnalyzer:
    def __init__(self):
        self.projects_dir = os.path.join(os.getcwd(), 'projects')

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
                            if diff.a_path and diff.a_path.endswith(('.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.ts', '.jsx', '.vue', '.html', '.css', '.scss', '.sql', '.yaml', '.yml', '.json', '.xml')):
                                if hasattr(diff, 'diff') and diff.diff:
                                    diff_text = diff.diff.decode('utf-8', errors='ignore')
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

    def save_analysis_report(self, df: pd.DataFrame, since_date: str, until_date: str) -> str:
        """Save the analysis report to a file with proper email-based grouping and fixed period formatting."""
        if df.empty:
            return None
            
        # Create timestamped output directory for this analysis run
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        main_dir = os.path.join(os.getcwd(), 'gitlab_reports')
        analysis_dir = os.path.join(main_dir, f'analysis_{timestamp}')
        os.makedirs(analysis_dir, exist_ok=True)
        
        report_file = os.path.join(analysis_dir, f'analysis_report_enhanced_{timestamp}.txt')
        csv_file = os.path.join(analysis_dir, f'analysis_report_enhanced_{timestamp}.csv')
        
        # Save text report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("Enhanced Git Repository Analysis Report (Email-Consolidated with Commit Frequency)\n")
            f.write("=" * 120 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Analysis Period: {since_date} to {until_date}\n")
            f.write("Scope: All Local Repositories\n")
            f.write("Note: Excluding merge commits and pull requests\n")
            f.write("Note: Authors grouped by email address to consolidate duplicate identities\n")
            f.write("=" * 120 + "\n\n")
            
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
        
        # Save CSV report
        df_csv = df.copy()
        df_csv.index.name = 'email'
        df_csv.to_csv(csv_file)
        
        print(f"\nEnhanced analysis reports saved to: {analysis_dir}")
        print(f"  - Text report: {os.path.basename(report_file)}")
        print(f"  - CSV report: {os.path.basename(csv_file)}")
        return analysis_dir

def parse_args():
    parser = argparse.ArgumentParser(description='Analyze local Git repositories with email-based author consolidation and commit frequency')
    parser.add_argument('--since', type=str, default=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'), 
                        help='Start date for analysis (YYYY-MM-DD)')
    parser.add_argument('--until', type=str, default=datetime.now().strftime('%Y-%m-%d'),
                        help='End date for analysis (YYYY-MM-DD)')
    parser.add_argument('--authors', type=str, nargs='+', help='Filter by specific authors (names or emails)')
    return parser.parse_args()

def main():
    print("Enhanced Local Git Repository Analyzer (Email-Consolidated with Commit Frequency)")
    print("=" * 100)
    
    args = parse_args()
    
    analyzer = LocalGitAnalyzer()
    
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
    
    if not df.empty:
        # Save report
        output_dir = analyzer.save_analysis_report(df, args.since, args.until)
        
        # Also print summary to console
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

if __name__ == "__main__":
    main() 