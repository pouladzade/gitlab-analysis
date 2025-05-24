#!/usr/bin/env python3

import os
import gitlab
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, List
import argparse

# Load environment variables
load_dotenv()

class GitLabIssueExporter:
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
        self.issues_dir = os.path.join(main_dir, f'issues_export_{timestamp}')
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
                        'id': issue.id,
                        'iid': issue.iid,
                        'title': issue.title,
                        'description': issue.description or '',
                        'web_url': issue.web_url,
                        'state': issue.state,
                        'created_at': issue.created_at,
                        'updated_at': issue.updated_at,
                        'author': issue.author['name'] if issue.author else 'Unknown',
                        'assignees': [assignee['name'] for assignee in issue.assignees] if issue.assignees else [],
                        'labels': issue.labels if hasattr(issue, 'labels') else [],
                        'milestone': issue.milestone['title'] if issue.milestone else None
                    }
                    recent_issues.append(issue_data)
            
            return recent_issues
            
        except Exception as e:
            print(f"Error fetching issues for project {project.name}: {str(e)}")
            return []

    def export_project_issues(self, project, days_back: int = 60) -> str:
        """Export issues for a single project to a file."""
        print(f"Fetching recent issues for: {project.name}")
        
        issues = self.get_recent_open_issues(project, days_back)
        
        if not issues:
            print(f"  No recent issues found for {project.name}")
            return None
            
        # Create safe filename from project name
        safe_name = "".join(c for c in project.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_issues_{timestamp}.md"
        filepath = os.path.join(self.issues_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Recent Open Issues - {project.name}\n\n")
            f.write(f"**Project:** {project.name}\n")
            f.write(f"**Project URL:** {project.web_url}\n")
            f.write(f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Issues from last {days_back} days:** {len(issues)}\n\n")
            f.write("---\n\n")
            
            for i, issue in enumerate(issues, 1):
                f.write(f"## {i}. {issue['title']}\n\n")
                f.write(f"**Issue ID:** #{issue['iid']}\n")
                f.write(f"**Link:** {issue['web_url']}\n")
                f.write(f"**Author:** {issue['author']}\n")
                f.write(f"**Created:** {issue['created_at']}\n")
                f.write(f"**Updated:** {issue['updated_at']}\n")
                
                if issue['assignees']:
                    f.write(f"**Assignees:** {', '.join(issue['assignees'])}\n")
                
                if issue['labels']:
                    f.write(f"**Labels:** {', '.join(issue['labels'])}\n")
                
                if issue['milestone']:
                    f.write(f"**Milestone:** {issue['milestone']}\n")
                
                f.write(f"**Status:** {issue['state']}\n\n")
                
                if issue['description']:
                    f.write("**Description:**\n")
                    f.write(f"{issue['description']}\n\n")
                else:
                    f.write("*No description provided*\n\n")
                
                f.write("---\n\n")
        
        print(f"  Exported {len(issues)} issues to: {filename}")
        return filepath

    def export_local_repository_issues(self, days_back: int = 60) -> List[str]:
        """Export issues from locally cloned repositories."""
        print(f"Scanning local repositories and fetching their recent issues...")
        
        projects_dir = os.path.join(os.getcwd(), 'projects')
        if not os.path.exists(projects_dir):
            print(f"Projects directory not found: {projects_dir}")
            return []
            
        exported_files = []
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
                                
                                filepath = self.export_project_issues(project, days_back)
                                if filepath:
                                    exported_files.append(filepath)
                                    
                            except gitlab.exceptions.GitlabGetError:
                                print(f"Could not access GitLab project: {project_path}")
                                continue
                            except Exception as e:
                                print(f"Error processing GitLab project {project_path}: {str(e)}")
                                continue
                                
                except Exception as e:
                    print(f"Error processing local repository {root}: {str(e)}")
                    continue
                    
        return exported_files

    def create_summary_file(self, exported_files: List[str], days_back: int):
        """Create a summary file with links to all exported issue files."""
        if not exported_files:
            print("No issues were exported.")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = os.path.join(self.issues_dir, f'issues_summary_{timestamp}.md')
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# GitLab Issues Export Summary\n\n")
            f.write(f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Period:** Recent open issues from last {days_back} days\n")
            f.write(f"**Total Files:** {len(exported_files)}\n\n")
            f.write("## Exported Files\n\n")
            
            for filepath in exported_files:
                filename = os.path.basename(filepath)
                f.write(f"- [{filename}](./{filename})\n")
                
        print(f"\nSummary file created: {os.path.basename(summary_file)}")
        print(f"Total exported files: {len(exported_files)}")

def parse_args():
    parser = argparse.ArgumentParser(description='Export recent open issues from GitLab repositories')
    parser.add_argument('--days', type=int, default=60, 
                        help='Number of days back to look for recent issues (default: 60)')
    return parser.parse_args()

def main():
    print("GitLab Recent Issues Exporter")
    print("=" * 40)
    
    args = parse_args()
    
    # Check for GitLab private token
    private_token = os.getenv('GITLAB_TOKEN')
    if not private_token:
        print("ERROR: GitLab private token not found.")
        print("Please set the GITLAB_TOKEN environment variable.")
        print("You can generate a personal access token in GitLab:")
        print("  Profile → Access Tokens → Personal Access Tokens")
        print("  Required scopes: api, read_repository")
        return 1
    
    try:
        exporter = GitLabIssueExporter(private_token=private_token)
        exported_files = exporter.export_local_repository_issues(args.days)
        exporter.create_summary_file(exported_files, args.days)
        
        print(f"\nMarkdown files exported to: {exporter.issues_dir}")
        print("All recent open issues have been exported successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 