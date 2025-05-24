#!/usr/bin/env python3

import os
import git
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import argparse

class LocalGitAnalyzer:
    def __init__(self):
        self.projects_dir = os.path.join(os.getcwd(), 'projects')
        
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
        """Analyze a single repository and return author statistics grouped by email."""
        repo = git.Repo(repo_path)
        
        # Get all commits in the date range
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
                stats[author_key] = {
                    'added': 0, 
                    'removed': 0, 
                    'commit_count': 0,
                    'commit_dates': [],
                    'active_days': set()
                }
                # Store the most common name for this email (first occurrence for now)
                email_to_name[author_key] = author_name
            
            # Track commit count and dates
            stats[author_key]['commit_count'] += 1
            commit_date = commit.committed_datetime.date()
            stats[author_key]['commit_dates'].append(commit_date)
            stats[author_key]['active_days'].add(commit_date)
            
            if commit.parents:
                # Use commit.stats to get total insertions/deletions
                file_stats = commit.stats.files
                for file_path, file_stat in file_stats.items():
                    if file_path.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.go', '.rb', '.php', '.swift', '.kt', '.rs')):
                        stats[author_key]['added'] += file_stat.get('insertions', 0)
                        stats[author_key]['removed'] += file_stat.get('deletions', 0)
        
        # Calculate commit frequency metrics and return stats with email-to-name mapping included
        for email, author_stats in stats.items():
            author_stats['name'] = email_to_name[email]
            author_stats['email'] = email
            
            # Calculate commit frequency metrics
            if author_stats['commit_dates']:
                first_commit = min(author_stats['commit_dates'])
                last_commit = max(author_stats['commit_dates'])
                total_days = (last_commit - first_commit).days + 1
                active_days_count = len(author_stats['active_days'])
                
                author_stats['first_commit'] = first_commit
                author_stats['last_commit'] = last_commit
                author_stats['active_days_count'] = active_days_count
                author_stats['total_days'] = total_days
                author_stats['avg_commits_per_day'] = author_stats['commit_count'] / total_days if total_days > 0 else 0
                author_stats['avg_commits_per_active_day'] = author_stats['commit_count'] / active_days_count if active_days_count > 0 else 0
            else:
                author_stats['first_commit'] = None
                author_stats['last_commit'] = None
                author_stats['active_days_count'] = 0
                author_stats['total_days'] = 0
                author_stats['avg_commits_per_day'] = 0
                author_stats['avg_commits_per_active_day'] = 0
            
            # Clean up temporary data
            del author_stats['commit_dates']
            del author_stats['active_days']
        
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
                # Analyze repository
                repo_stats = self.analyze_repository(repo_path, since_date, until_date, authors)
                
                # Accumulate stats (now using email as key)
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
                            'total_days': stats['total_days']
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
        """Save the analysis report to a file with proper email-based grouping."""
        if df.empty:
            return None
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(self.projects_dir, f'ptc_telematik_analysis_report_consolidated_{timestamp}.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("PTC Telematik GitLab - Lines Added/Removed Report (Email-Consolidated Analysis)\n")
            f.write("=" * 100 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"GitLab Instance: https://gitlab.ptc-telematik.de\n")
            f.write(f"Analysis Period: {since_date} to {until_date}\n")
            f.write("Scope: All Local Repositories\n")
            f.write("Note: Excluding merge commits and pull requests\n")
            f.write("Note: Authors grouped by email address to consolidate duplicate identities\n")
            f.write("=" * 100 + "\n\n")
            
            # Write summary statistics
            f.write("SUMMARY STATISTICS:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Authors: {len(df)}\n")
            f.write(f"Total Lines Added: {df['added'].sum():,}\n")
            f.write(f"Total Lines Removed: {df['removed'].sum():,}\n")
            f.write(f"Net Lines Added: {df['net'].sum():,}\n")
            f.write("\n")
            
                        # Write detailed report            f.write("DETAILED REPORT BY AUTHOR (CONSOLIDATED BY EMAIL):\n")            f.write("-" * 140 + "\n")            f.write(f"{'Author (Email)':<40} | {'Added':>8} | {'Removed':>8} | {'Net':>8} | {'Commits':>7} | {'Avg/Day':>7} | {'Act.Days':>8} | {'Period':>12}\n")            f.write("-" * 140 + "\n")                        for author_email, row in df.iterrows():                # Format as "Name (email)" for display                author_display = f"{row['name']} ({author_email})"                if len(author_display) > 40:                    author_display = author_display[:37] + "..."                                # Format date range                if row['first_commit'] and row['last_commit']:                    if row['first_commit'] == row['last_commit']:                        period = row['first_commit'].strftime('%Y-%m-%d')                    else:                        period = f"{row['first_commit'].strftime('%m/%d')}-{row['last_commit'].strftime('%m/%d')}"                else:                    period = "N/A"                                f.write(f"{author_display:<40} | {row['added']:>8} | {row['removed']:>8} | {row['net']:>8} | {row['commit_count']:>7} | {row['avg_commits_per_day']:>7.2f} | {row['active_days_count']:>8} | {period:>12}\n")
                
            f.write("\n" + "=" * 100 + "\n")
            f.write("Report generated by Local Git Analyzer (Email-Consolidated Version)\n")
        
        print(f"\nAnalysis report saved to: {report_file}")
        return report_file

def parse_args():
    parser = argparse.ArgumentParser(description='Analyze local Git repositories with email-based author consolidation')
    parser.add_argument('--since', type=str, default=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'), 
                        help='Start date for analysis (YYYY-MM-DD)')
    parser.add_argument('--until', type=str, default=datetime.now().strftime('%Y-%m-%d'),
                        help='End date for analysis (YYYY-MM-DD)')
    parser.add_argument('--authors', type=str, nargs='+', help='Filter by specific authors (names or emails)')
    return parser.parse_args()

def main():
    print("Local Git Repository Analyzer (Email-Consolidated Version)")
    print("=" * 80)
    
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
        analyzer.save_analysis_report(df, args.since, args.until)
        
                # Also print summary to console        print("\nCONSOLIDATED SUMMARY (Email-Grouped with Commit Frequency):")        print("-" * 140)        print(f"{'Author (Email)':<40} | {'Added':>8} | {'Removed':>8} | {'Net':>8} | {'Commits':>7} | {'Avg/Day':>7} | {'Act.Days':>8} | {'Period':>12}")        print("-" * 140)                for author_email, row in df.iterrows():            author_display = f"{row['name']} ({author_email})"            if len(author_display) > 40:                author_display = author_display[:37] + "..."                        # Format date range            if row['first_commit'] and row['last_commit']:                if row['first_commit'] == row['last_commit']:                    period = row['first_commit'].strftime('%Y-%m-%d')                else:                    period = f"{row['first_commit'].strftime('%m/%d')}-{row['last_commit'].strftime('%m/%d')}"            else:                period = "N/A"                        print(f"{author_display:<40} | {row['added']:>8} | {row['removed']:>8} | {row['net']:>8} | {row['commit_count']:>7} | {row['avg_commits_per_day']:>7.2f} | {row['active_days_count']:>8} | {period:>12}")
    else:
        print("No analysis data generated.")

if __name__ == "__main__":
    main() 