#!/usr/bin/env python3

import os
import csv
import gitlab
from datetime import datetime, timedelta
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GitLabToJiraExporter:
    def __init__(self, gitlab_url: str = None, private_token: str = None):
        self.gitlab_url = gitlab_url or os.getenv('GITLAB_URL', 'https://gitlab.example.com')
        self.private_token = private_token or os.getenv('GITLAB_TOKEN')
        
        if not self.private_token:
            raise ValueError("GitLab private token not found. Set GITLAB_TOKEN environment variable.")
        
        # Initialize GitLab connection
        self.gl = gitlab.Gitlab(self.gitlab_url, private_token=self.private_token)
        self.gl.auth()
        
        # Create timestamped output directory for this export run
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        main_dir = os.path.join(os.getcwd(), 'gitlab_reports')
        self.issues_dir = os.path.join(main_dir, f'jira_{timestamp}')
        os.makedirs(self.issues_dir, exist_ok=True)
        
        print(f"Successfully connected to GitLab instance: {self.gitlab_url}")
        print(f"Export directory: {self.issues_dir}")

    def map_status_to_jira(self, gitlab_state: str, labels: List[str] = None) -> str:
        """Map GitLab issue state and labels to Jira status."""
        labels = labels or []
        label_text = ' '.join(labels).lower()
        
        if gitlab_state == 'closed':
            return 'Done'
        elif any(keyword in label_text for keyword in ['wip', 'in progress', 'doing']):
            return 'In Progress'
        elif any(keyword in label_text for keyword in ['review', 'testing', 'qa']):
            return 'In Review'
        else:
            return 'To Do'

    def map_issue_type(self, labels: List[str] = None, title: str = '') -> str:
        """Map GitLab labels and title to Jira issue type."""
        labels = labels or []
        all_text = (' '.join(labels) + ' ' + title).lower()
        
        if any(keyword in all_text for keyword in ['bug', 'error', 'fix', 'defect']):
            return 'Bug'
        elif any(keyword in all_text for keyword in ['epic']):
            return 'Epic'
        elif any(keyword in all_text for keyword in ['spike', 'research', 'investigation']):
            return 'Spike'
        elif any(keyword in all_text for keyword in ['feature', 'story', 'user story']):
            return 'Story'
        else:
            return 'Task'

    def map_priority(self, labels: List[str] = None, title: str = '') -> str:
        """Map GitLab labels and title to Jira priority."""
        labels = labels or []
        all_text = (' '.join(labels) + ' ' + title).lower()
        
        if any(keyword in all_text for keyword in ['high', 'urgent', 'critical', 'blocker']):
            return 'High'
        elif any(keyword in all_text for keyword in ['low', 'minor']):
            return 'Low'
        else:
            return 'Medium'

    def extract_components(self, labels: List[str] = None, repository_name: str = '') -> str:
        """Extract component names from labels and repository name."""
        labels = labels or []
        components = []
        
        # Common component patterns in labels
        component_keywords = ['frontend', 'backend', 'api', 'ui', 'database', 'infrastructure', 'auth']
        
        for label in labels:
            label_lower = label.lower()
            if any(keyword in label_lower for keyword in component_keywords):
                if label not in components:
                    components.append(label)
        
        # Add repository name as a component if no specific components found
        if not components and repository_name:
            components.append(repository_name)
        
        return ', '.join(components)

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

    def get_recent_open_issues(self, project, days_back: int = 60) -> List[Dict]:
        """Fetch recent open issues from a GitLab project and convert to Jira format."""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
        
        try:
            # Get all open issues
            issues = project.issues.list(state='opened', all=True)
            
            jira_issues = []
            for issue in issues:
                # Simple date string comparison to avoid timezone issues
                created_date = issue.created_at[:10]  # Extract YYYY-MM-DD
                updated_date = issue.updated_at[:10]  # Extract YYYY-MM-DD
                
                if created_date >= cutoff_date_str or updated_date >= cutoff_date_str:
                    labels = issue.labels if hasattr(issue, 'labels') and issue.labels else []
                    
                    # Build comprehensive description with user context
                    description_parts = []
                    
                    # Add original description
                    original_description = (issue.description or '').strip()
                    if original_description:
                        description_parts.append(original_description)
                    
                    # Add creator information
                    creator_info = f"Created by: {self.format_user_info(issue.author)}"
                    if issue.created_at:
                        creator_info += f" on {issue.created_at[:19].replace('T', ' ')}"
                    
                    # Add assignee information if any
                    assignee_info = ""
                    if issue.assignees:
                        assignee_names = [self.format_user_info(assignee) for assignee in issue.assignees]
                        assignee_info = f"Assigned to: {', '.join(assignee_names)}"
                    
                    # Get comments/notes and include user names
                    comments_section = ""
                    try:
                        notes = issue.notes.list(all=True)
                        if notes:
                            comment_list = []
                            for note in notes:
                                if hasattr(note, 'body') and note.body.strip():
                                    note_author = self.format_user_info(getattr(note, 'author', None))
                                    created_date = getattr(note, 'created_at', '')
                                    if created_date:
                                        created_date = created_date[:19].replace('T', ' ')  # Format: YYYY-MM-DD HH:MM:SS
                                    
                                    comment_list.append(f"[{created_date}] {note_author}:\n{note.body}")
                            
                            if comment_list:
                                comments_section = "--- COMMENTS ---\n" + "\n\n".join(comment_list)
                    except Exception:
                        # If we can't fetch comments, continue without them
                        pass
                    
                    # Build final description
                    final_parts = [creator_info]
                    if assignee_info:
                        final_parts.append(assignee_info)
                    if original_description:
                        final_parts.append(f"Description:\n{original_description}")
                    if comments_section:
                        final_parts.append(comments_section)
                    
                    # Add original GitLab link
                    final_parts.append(f"Original GitLab Issue: {issue.web_url}")
                    
                    description = "\n\n".join(final_parts)
                    
                    # Prepare assignee (Jira expects single assignee, use email for user matching)
                    assignee = ''
                    if issue.assignees:
                        # Use email address if available, fallback to username
                        if 'email' in issue.assignees[0]:
                            assignee = issue.assignees[0]['email']
                        else:
                            assignee = issue.assignees[0]['username']
                    
                    # Use email for reporter as well
                    reporter = 'Unknown'
                    if issue.author:
                        if 'email' in issue.author:
                            reporter = issue.author['email']
                        else:
                            reporter = issue.author['username']
                    
                    jira_issue = {
                        'Issue Type': self.map_issue_type(labels, issue.title),
                        'Summary': issue.title,
                        'Description': description,
                        'Status': self.map_status_to_jira(issue.state, labels),
                        'Priority': self.map_priority(labels, issue.title),
                        'Reporter': reporter,
                        'Assignee': assignee,
                        'Labels': ', '.join(labels),
                        'Components': self.extract_components(labels, project.name),
                        'Fix Version': issue.milestone['title'] if issue.milestone else '',
                        'Story Points': getattr(issue, 'weight', ''),
                        'Due Date': getattr(issue, 'due_date', ''),
                        'Created': issue.created_at,
                        'Updated': issue.updated_at,
                        'External ID': f"gitlab-{issue.id}",
                        'Original URL': issue.web_url,
                        'Repository': project.name,
                        'GitLab Issue ID': issue.iid,
                        'Upvotes': getattr(issue, 'upvotes', 0),
                        'Downvotes': getattr(issue, 'downvotes', 0)
                    }
                    jira_issues.append(jira_issue)
            
            return jira_issues
            
        except Exception as e:
            print(f"Error fetching issues for project {project.name}: {str(e)}")
            return []

    def export_project_issues_jira(self, project, days_back: int = 60) -> str:
        """Export issues for a single project to a Jira-compatible CSV file."""
        print(f"Fetching recent issues for: {project.name}")
        
        issues = self.get_recent_open_issues(project, days_back)
        
        if not issues:
            print(f"  No recent issues found for {project.name}")
            return None
            
        # Create safe filename from project name
        safe_name = "".join(c for c in project.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_jira_import_{timestamp}.csv"
        filepath = os.path.join(self.issues_dir, filename)
        
        # Define Jira CSV headers (order matters for import)
        headers = [
            'Issue Type', 'Summary', 'Description', 'Status', 'Priority', 'Reporter',
            'Assignee', 'Labels', 'Components', 'Fix Version', 'Story Points', 'Due Date',
            'Created', 'Updated', 'External ID', 'Original URL', 'Repository', 
            'GitLab Issue ID', 'Upvotes', 'Downvotes'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(issues)
        
        print(f"  Exported {len(issues)} issues to: {filename}")
        return filepath

    def export_all_repositories_jira(self, days_back: int = 60) -> List[str]:
        """Export issues from all locally cloned repositories as Jira-compatible CSV files."""
        print(f"Scanning local repositories and fetching their recent issues for Jira import...")
        
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
                                    filepath = self.export_project_issues_jira(project, days_back)
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
        
        # Create consolidated Jira import CSV file
        if all_issues:
            self.create_consolidated_jira_csv(all_issues, days_back)
                    
        return exported_files

    def create_consolidated_jira_csv(self, all_issues: List[Dict], days_back: int):
        """Create a consolidated Jira-compatible CSV file with all issues from all repositories."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        consolidated_file = os.path.join(self.issues_dir, f'all_issues_jira_import_{timestamp}.csv')
        
        # Define Jira CSV headers
        headers = [
            'Issue Type', 'Summary', 'Description', 'Status', 'Priority', 'Reporter',
            'Assignee', 'Labels', 'Components', 'Fix Version', 'Story Points', 'Due Date',
            'Created', 'Updated', 'External ID', 'Original URL', 'Repository', 
            'GitLab Issue ID', 'Upvotes', 'Downvotes'
        ]
        
        with open(consolidated_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_issues)
        
        print(f"\nConsolidated Jira Import CSV created: {os.path.basename(consolidated_file)}")
        print(f"Total issues across all repositories: {len(all_issues)}")
        
        # Print statistics about the export
        self.print_export_statistics(all_issues)

    def print_export_statistics(self, issues: List[Dict]):
        """Print statistics about the exported issues."""
        if not issues:
            return
            
        print(f"\n" + "=" * 60)
        print("EXPORT STATISTICS:")
        print("=" * 60)
        
        # Count by issue type
        issue_types = {}
        statuses = {}
        priorities = {}
        repositories = {}
        
        for issue in issues:
            issue_type = issue.get('Issue Type', 'Unknown')
            status = issue.get('Status', 'Unknown')
            priority = issue.get('Priority', 'Unknown')
            repo = issue.get('Repository', 'Unknown')
            
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            statuses[status] = statuses.get(status, 0) + 1
            priorities[priority] = priorities.get(priority, 0) + 1
            repositories[repo] = repositories.get(repo, 0) + 1
        
        print(f"By Issue Type:")
        for issue_type, count in sorted(issue_types.items()):
            print(f"  {issue_type}: {count}")
        
        print(f"\nBy Status:")
        for status, count in sorted(statuses.items()):
            print(f"  {status}: {count}")
        
        print(f"\nBy Priority:")
        for priority, count in sorted(priorities.items()):
            print(f"  {priority}: {count}")
        
        print(f"\nBy Repository:")
        for repo, count in sorted(repositories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {repo}: {count}")

    def create_summary_file(self, exported_files: List[str], days_back: int):
        """Create a summary file with information about exported Jira CSV files."""
        if not exported_files:
            print("No issues were exported.")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = os.path.join(self.issues_dir, f'jira_import_summary_{timestamp}.txt')
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"GitLab to Jira Issues Export Summary\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Export period: Last {days_back} days\n")
            f.write(f"Total exported files: {len(exported_files)}\n")
            f.write(f"Export directory: {self.issues_dir}\n\n")
            
            f.write("Exported Files:\n")
            f.write("-" * 30 + "\n")
            for i, filepath in enumerate(exported_files, 1):
                filename = os.path.basename(filepath)
                f.write(f"{i}. {filename}\n")
            
            f.write(f"\nFor Jira import:\n")
            f.write(f"1. Use the consolidated CSV file for bulk import\n")
            f.write(f"2. In Jira: System → External System Import → CSV\n")
            f.write(f"3. Map CSV columns to Jira fields\n")
            f.write(f"4. Review and confirm import\n")
            f.write(f"\nNote: Issues include full context with user names in descriptions and comments\n")
        
        print(f"Summary file created: {os.path.basename(summary_file)}")
        print(f"Total exported Jira CSV files: {len(exported_files)}")

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Export GitLab issues to Jira-compatible CSV format with user context')
    parser.add_argument('--days', type=int, default=60, help='Number of days back to look for recent issues (default: 60)')
    return parser.parse_args()

def main():
    print("GitLab to Jira Issues CSV Exporter (with User Context)")
    print("=" * 55)
    
    args = parse_args()
    
    try:
        exporter = GitLabToJiraExporter()
        exported_files = exporter.export_all_repositories_jira(args.days)
        exporter.create_summary_file(exported_files, args.days)
        
        print(f"\nJira-compatible CSV files exported to: {exporter.issues_dir}")
        print("Ready for Jira import! Issues include full user context in descriptions.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 