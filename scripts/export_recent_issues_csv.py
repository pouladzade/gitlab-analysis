#!/usr/bin/env python3

import os
import gitlab
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, List
import argparse

# Load environment variables
load_dotenv()

class GitLabIssueCSVExporter:
    def __init__(self, gitlab_url: str = None, private_token: str = None):
        self.ssh_url = gitlab_url or 'git@gitlab.ptc-telematik.de'
        self.api_url = 'https://gitlab.ptc-telematik.de'
        
        try:
            self.gl = gitlab.Gitlab(self.api_url, private_token=private_token)
            self.gl.auth()
            print(f"Successfully connected to GitLab instance: {self.api_url}")
        except Exception as e:
            print(f"Error connecting to GitLab instance {self.api_url}: {str(e)}")
            raise
            
        # Create timestamped output directory for this export run
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        main_dir = os.path.join(os.getcwd(), 'gitlab_reports')
        self.issues_dir = os.path.join(main_dir, f'issues_csv_{timestamp}')
        os.makedirs(self.issues_dir, exist_ok=True)
        
        print(f"Export directory: {self.issues_dir}")

    def get_recent_open_issues(self, project, days_back: int = 60) -> List[Dict]:
        """Fetch recent open issues from a GitLab project."""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
        
        try:
            # Get all open issues
            issues = project.issues.list(state='opened', all=True)
            
            recent_issues = []
            for issue in issues:
                # Simple date string comparison to avoid timezone issues
                created_date = issue.created_at[:10]  # Extract YYYY-MM-DD
                updated_date = issue.updated_at[:10]  # Extract YYYY-MM-DD
                
                if created_date >= cutoff_date_str or updated_date >= cutoff_date_str:
                    issue_data = {
                        'repository': project.name,
                        'project_url': project.web_url,
                        'issue_id': issue.id,
                        'issue_iid': issue.iid,
                        'title': issue.title,
                        'description': (issue.description or '').replace('\n', ' ').replace('\r', ' ').strip(),
                        'web_url': issue.web_url,
                        'state': issue.state,
                        'created_at': issue.created_at,
                        'updated_at': issue.updated_at,
                        'author': issue.author['name'] if issue.author else 'Unknown',
                        'author_username': issue.author['username'] if issue.author else '',
                        'assignees': ', '.join([assignee['name'] for assignee in issue.assignees]) if issue.assignees else '',
                        'assignee_usernames': ', '.join([assignee['username'] for assignee in issue.assignees]) if issue.assignees else '',
                        'labels': ', '.join(issue.labels) if hasattr(issue, 'labels') and issue.labels else '',
                        'milestone': issue.milestone['title'] if issue.milestone else '',
                        'due_date': getattr(issue, 'due_date', ''),
                        'weight': getattr(issue, 'weight', ''),
                        'upvotes': getattr(issue, 'upvotes', 0),
                        'downvotes': getattr(issue, 'downvotes', 0)
                    }
                    recent_issues.append(issue_data)
            
            return recent_issues
            
        except Exception as e:
            print(f"Error fetching issues for project {project.name}: {str(e)}")
            return []

    def export_project_issues_csv(self, project, days_back: int = 60) -> str:
        """Export issues for a single project to a CSV file."""
        print(f"Fetching recent issues for: {project.name}")
        
        issues = self.get_recent_open_issues(project, days_back)
        
        if not issues:
            print(f"  No recent issues found for {project.name}")
            return None
            
        # Create safe filename from project name
        safe_name = "".join(c for c in project.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_issues_{timestamp}.csv"
        filepath = os.path.join(self.issues_dir, filename)
        
        # Define CSV headers
        headers = [
            'repository', 'project_url', 'issue_id', 'issue_iid', 'title', 'description',
            'web_url', 'state', 'created_at', 'updated_at', 'author', 'author_username',
            'assignees', 'assignee_usernames', 'labels', 'milestone', 'due_date', 
            'weight', 'upvotes', 'downvotes'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(issues)
        
        print(f"  Exported {len(issues)} issues to: {filename}")
        return filepath

    def export_local_repository_issues_csv(self, days_back: int = 60) -> List[str]:
        """Export issues from locally cloned repositories as CSV files."""
        print(f"Scanning local repositories and fetching their recent issues...")
        
        projects_dir = os.path.join(os.getcwd(), 'projects')
        if not os.path.exists(projects_dir):
            print(f"Projects directory not found: {projects_dir}")
            return []
            
        exported_files = []
        all_issues = []  # For consolidated CSV
        processed_projects = set()
        
        for root, dirs, files in os.walk(projects_dir):
            if '.git' in dirs:
                try:
                    import git
                    repo = git.Repo(root)
                    
                    if 'origin' in repo.remotes:
                        remote_url = repo.remotes.origin.url
                        
                        if 'gitlab' in remote_url:
                            if remote_url.startswith('git@'):
                                project_path = remote_url.split(':')[1].replace('.git', '')
                            else:
                                project_path = '/'.join(remote_url.split('/')[-2:]).replace('.git', '')
                            
                            if project_path in processed_projects:
                                continue
                                
                            processed_projects.add(project_path)
                            
                            try:
                                project = self.gl.projects.get(project_path)
                                print(f"Found GitLab project: {project_path}")
                                
                                # Get issues for this project
                                issues = self.get_recent_open_issues(project, days_back)
                                if issues:
                                    # Export individual CSV file
                                    filepath = self.export_project_issues_csv(project, days_back)
                                    if filepath:
                                        exported_files.append(filepath)
                                    
                                    # Add to consolidated list
                                    all_issues.extend(issues)
                                    
                            except gitlab.exceptions.GitlabGetError:
                                print(f"Could not access GitLab project: {project_path}")
                                continue
                            except Exception as e:
                                print(f"Error processing GitLab project {project_path}: {str(e)}")
                                continue
                                
                except Exception as e:
                    print(f"Error processing local repository {root}: {str(e)}")
                    continue
        
        # Create consolidated CSV file
        if all_issues:
            self.create_consolidated_csv(all_issues, days_back)
                    
        return exported_files

    def create_consolidated_csv(self, all_issues: List[Dict], days_back: int):
        """Create a consolidated CSV file with all issues from all repositories."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        consolidated_file = os.path.join(self.issues_dir, f'all_issues_consolidated_{timestamp}.csv')
        
        # Define CSV headers
        headers = [
            'repository', 'project_url', 'issue_id', 'issue_iid', 'title', 'description',
            'web_url', 'state', 'created_at', 'updated_at', 'author', 'author_username',
            'assignees', 'assignee_usernames', 'labels', 'milestone', 'due_date', 
            'weight', 'upvotes', 'downvotes'
        ]
        
        with open(consolidated_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_issues)
        
        print(f"\nConsolidated CSV created: {os.path.basename(consolidated_file)}")
        print(f"Total issues across all repositories: {len(all_issues)}")

    def create_summary_file(self, exported_files: List[str], days_back: int):
        """Create a summary file with information about exported CSV files."""
        if not exported_files:
            print("No issues were exported.")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = os.path.join(self.issues_dir, f'csv_export_summary_{timestamp}.txt')
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"GitLab Issues CSV Export Summary\n")
            f.write(f"=" * 50 + "\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Period: Recent open issues from last {days_back} days\n")
            f.write(f"Total Files: {len(exported_files)}\n\n")
            f.write("Exported CSV Files:\n")
            f.write("-" * 30 + "\n")
            
            for filepath in exported_files:
                filename = os.path.basename(filepath)
                f.write(f"- {filename}\n")
                
        print(f"\nSummary file created: {os.path.basename(summary_file)}")
        print(f"Total exported CSV files: {len(exported_files)}")

def parse_args():
    parser = argparse.ArgumentParser(description='Export recent open issues from GitLab repositories as CSV files')
    parser.add_argument('--days', type=int, default=60, 
                        help='Number of days back to look for recent issues (default: 60)')
    parser.add_argument('--local-repos', action='store_true',
                        help='Export issues from locally cloned repositories only')
    return parser.parse_args()

def main():
    print("GitLab Recent Issues CSV Exporter")
    print("=" * 50)
    
    args = parse_args()
    
    gitlab_url = os.getenv('GITLAB_URL', 'git@gitlab.ptc-telematik.de')
    private_token = os.getenv('GITLAB_TOKEN')
    
    if not private_token:
        print("Error: GITLAB_TOKEN environment variable is not set")
        print("Please set your GitLab personal access token in the .env file:")
        print("GITLAB_TOKEN=your_personal_access_token")
        return
    
    try:
        exporter = GitLabIssueCSVExporter(gitlab_url, private_token)
    except Exception as e:
        print(f"Error initializing GitLab issue CSV exporter: {str(e)}")
        return
    
    exported_files = exporter.export_local_repository_issues_csv(args.days)
    exporter.create_summary_file(exported_files, args.days)
    
    print(f"\nCSV files exported to directory: {exporter.issues_dir}")

if __name__ == "__main__":
    main() 