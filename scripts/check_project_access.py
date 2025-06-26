#!/usr/bin/env python3

import os
import gitlab
from dotenv import load_dotenv

# Load environment variables from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

def check_project_access():
    # Get GitLab URL and token from environment
    gitlab_url = os.getenv('GITLAB_URL')
    gitlab_token = os.getenv('GITLAB_TOKEN')
    
    if not gitlab_url:
        print("Error: GITLAB_URL not found in environment variables")
        print("Please set GITLAB_URL in your .env file")
        return
    
    if not gitlab_token:
        print("Error: GITLAB_TOKEN not found in environment variables")
        print("Please set GITLAB_TOKEN in your .env file")
        return
    
    print(f"Connecting to GitLab instance: {gitlab_url}")
    
    # Initialize GitLab connection
    gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
    gl.auth()
    
    print("Current user permissions:")
    print(f"Username: {gl.user.username}")
    print(f"Name: {gl.user.name}")
    print(f"Email: {gl.user.email}")
    
    print("\nChecking Maintenance group projects...")
    try:
        maintenance_group = gl.groups.get('maintenance')
        print(f"\nProjects in Maintenance group:")
        for project in maintenance_group.projects.list(all=True):
            print(f"- {project.path_with_namespace}")
    except gitlab.exceptions.GitlabGetError as e:
        print(f"\nError accessing Maintenance group: {str(e)}")
        print("\nTrying alternative group ID...")
        try:
            maintenance_group = gl.groups.get(364)  # Using the ID we found earlier
            print(f"\nProjects in Maintenance group (ID: 364):")
            for project in maintenance_group.projects.list(all=True):
                print(f"- {project.path_with_namespace}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == '__main__':
    check_project_access() 