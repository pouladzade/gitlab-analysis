#!/usr/bin/env python3
"""
GitLab Registry Package Lister

This script lists all packages and libraries in GitLab Package Registry.
Supports various package types: npm, PyPI, Maven, NuGet, Composer, etc.
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from dotenv import load_dotenv

# Fix .env loading by finding the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Add the src directory to the path
sys.path.append(os.path.join(project_root, 'src'))
from gitlab_utils import GitLabClient, GitLabConfig

# Load environment variables
load_dotenv(env_path)


class PackageType(Enum):
    """Enum for supported package types in GitLab Package Registry."""
    NPM = "npm"
    PYPI = "pypi"
    MAVEN = "maven"
    NUGET = "nuget"
    COMPOSER = "composer"
    GENERIC = "generic"
    CONAN = "conan"
    HELM = "helm"
    TERRAFORM = "terraform"
    DEBIAN = "debian"
    RPM = "rpm"
    RUBYGEMS = "rubygems"


class OutputFormat(Enum):
    """Enum for output formats."""
    JSON = "json"
    CSV = "csv"
    TABLE = "table"
    SUMMARY = "summary"


class SortBy(Enum):
    """Enum for sorting options."""
    NAME = "name"
    TYPE = "type"
    PROJECT = "project"
    VERSION = "version"
    CREATED = "created"
    SIZE = "size"


def create_packages_report_directory() -> str:
    """Create a timestamped directory for package reports under gitlab_packages_report."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    main_dir = os.path.join(project_root, 'gitlab_packages_report')
    output_dir = os.path.join(main_dir, f'packages_report_{timestamp}')
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir


def create_safe_filename(name: str) -> str:
    """Create a safe filename from a project name."""
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    return safe_name.replace(' ', '_')


class GitLabRegistryLister:
    """Main class for listing GitLab registry packages."""
    
    def __init__(self, verbose: bool = False, debug: bool = False):
        """Initialize the GitLab registry lister."""
        self.verbose = verbose
        self.debug = debug
        
        if self.debug:
            print(f"Debug: Project root: {project_root}")
            print(f"Debug: .env path: {env_path}")
            print(f"Debug: .env exists: {os.path.exists(env_path)}")
            print(f"Debug: GITLAB_URL from env: {os.getenv('GITLAB_URL')}")
            print(f"Debug: GITLAB_TOKEN set: {'Yes' if os.getenv('GITLAB_TOKEN') else 'No'}")
            if os.getenv('GITLAB_TOKEN'):
                print(f"Debug: GITLAB_TOKEN length: {len(os.getenv('GITLAB_TOKEN'))}")
        
        try:
            self.config = GitLabConfig()
            self.client = GitLabClient(self.config)
        except Exception as e:
            if self.debug:
                print(f"Debug: Error during GitLab config/client creation: {e}")
            raise
        
        self.session = requests.Session()
        self.session.headers.update({
            'PRIVATE-TOKEN': self.config.gitlab_token,
            'Content-Type': 'application/json'
        })
        
        if self.verbose:
            print(f"Initialized GitLab Registry Lister for: {self.config.gitlab_url}")
    
    def get_project_packages(self, project_id: Union[int, str], 
                           package_type: Optional[PackageType] = None) -> List[Dict[str, Any]]:
        """Get packages for a specific project."""
        url = f"{self.config.gitlab_url}/api/v4/projects/{project_id}/packages"
        params = {}
        
        if package_type:
            params['package_type'] = package_type.value
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            packages = response.json()
            
            # Enhance package data with project info
            for package in packages:
                package['project_id'] = project_id
                
            return packages
            
        except requests.exceptions.RequestException as e:
            if self.verbose:
                try:
                    print(f"Error fetching packages for project {project_id}: {str(e)[:100]}")
                except:
                    print(f"Error fetching packages for project {project_id}: HTTP Error")
            return []
    
    def get_all_packages(self, package_type: Optional[PackageType] = None,
                        project_ids: Optional[List[Union[int, str]]] = None) -> List[Dict[str, Any]]:
        """Get all packages from GitLab registry."""
        all_packages = []
        
        if project_ids:
            # Get packages for specific projects
            projects_to_check = project_ids
        else:
            # Get all accessible projects
            try:
                projects = self.client.gl.projects.list(all=True, archived=False)
                projects_to_check = [project.id for project in projects]
                
                if self.verbose:
                    print(f"Found {len(projects_to_check)} projects to check for packages")
            except Exception as e:
                print(f"Error fetching projects: {e}")
                return []
        
        # Collect packages from all projects
        for project_id in projects_to_check:
            packages = self.get_project_packages(project_id, package_type)
            
            if packages and self.verbose:
                print(f"Found {len(packages)} packages in project {project_id}")
            
            all_packages.extend(packages)
        
        return all_packages
    
    def get_package_details(self, project_id: Union[int, str], package_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific package."""
        url = f"{self.config.gitlab_url}/api/v4/projects/{project_id}/packages/{package_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if self.verbose:
                try:
                    print(f"Error fetching package details for {package_id}: {str(e)[:100]}")
                except:
                    print(f"Error fetching package details for {package_id}: HTTP Error")
            return None
    
    def get_package_files(self, project_id: Union[int, str], package_id: int) -> List[Dict[str, Any]]:
        """Get files for a specific package."""
        url = f"{self.config.gitlab_url}/api/v4/projects/{project_id}/packages/{package_id}/package_files"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if self.verbose:
                try:
                    print(f"Error fetching package files for {package_id}: {str(e)[:100]}")
                except:
                    print(f"Error fetching package files for {package_id}: HTTP Error")
            return []
    
    def enhance_package_data(self, packages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance package data with additional details."""
        enhanced_packages = []
        
        for package in packages:
            enhanced = package.copy()
            
            # Get project details
            try:
                project = self.client.gl.projects.get(package['project_id'])
                enhanced['project_name'] = project.name
                enhanced['project_path'] = project.path_with_namespace
                enhanced['project_visibility'] = project.visibility
            except Exception:
                enhanced['project_name'] = f"Project {package['project_id']}"
                enhanced['project_path'] = f"project-{package['project_id']}"
                enhanced['project_visibility'] = "unknown"
            
            # Add package URL/link
            enhanced['package_url'] = self._get_package_url(enhanced)  # Use enhanced data with project_path
            enhanced['package_files_url'] = self._get_package_files_url(package)
            enhanced['project_registry_url'] = self._get_project_package_registry_url(enhanced)
            
            # Calculate package size if files are available
            package_files = self.get_package_files(package['project_id'], package['id'])
            total_size = sum(file.get('size', 0) for file in package_files)
            enhanced['total_size_bytes'] = total_size
            enhanced['total_size_mb'] = round(total_size / (1024 * 1024), 2) if total_size > 0 else 0
            enhanced['file_count'] = len(package_files)
            
            enhanced_packages.append(enhanced)
        
        return enhanced_packages
    
    def _get_package_url(self, package: Dict[str, Any]) -> str:
        """Generate the direct URL to the package in GitLab."""
        project_id = package.get('project_id')
        package_id = package.get('id')
        # Try to get project path for better URL, fallback to package ID
        project_path = package.get('project_path')
        if project_path:
            return f"{self.config.gitlab_url}/{project_path}/-/packages/{package_id}"
        else:
            return f"{self.config.gitlab_url}/-/packages/{package_id}"
    
    def _get_package_files_url(self, package: Dict[str, Any]) -> str:
        """Generate the URL to view package files in GitLab."""
        project_id = package.get('project_id')
        package_id = package.get('id')
        return f"{self.config.gitlab_url}/api/v4/projects/{project_id}/packages/{package_id}/package_files"
    
    def _get_project_package_registry_url(self, package: Dict[str, Any]) -> str:
        """Generate the URL to the project's package registry page."""
        project_path = package.get('project_path')
        if project_path:
            return f"{self.config.gitlab_url}/{project_path}/-/packages"
        else:
            project_id = package.get('project_id')
            return f"{self.config.gitlab_url}/projects/{project_id}/-/packages"
    
    def filter_packages(self, packages: List[Dict[str, Any]], 
                       package_types: Optional[List[PackageType]] = None,
                       search_term: Optional[str] = None) -> List[Dict[str, Any]]:
        """Filter packages based on criteria."""
        filtered = packages
        
        if package_types:
            type_values = [pt.value for pt in package_types]
            filtered = [p for p in filtered if p.get('package_type') in type_values]
        
        if search_term:
            search_lower = search_term.lower()
            filtered = [
                p for p in filtered 
                if (search_lower in p.get('name', '').lower() or 
                    search_lower in p.get('project_name', '').lower() or
                    search_lower in p.get('version', '').lower())
            ]
        
        return filtered
    
    def sort_packages(self, packages: List[Dict[str, Any]], 
                     sort_by: SortBy = SortBy.NAME, 
                     reverse: bool = False) -> List[Dict[str, Any]]:
        """Sort packages by specified criteria."""
        sort_key_map = {
            SortBy.NAME: lambda p: p.get('name', '').lower(),
            SortBy.TYPE: lambda p: p.get('package_type', ''),
            SortBy.PROJECT: lambda p: p.get('project_name', '').lower(),
            SortBy.VERSION: lambda p: p.get('version', ''),
            SortBy.CREATED: lambda p: p.get('created_at', ''),
            SortBy.SIZE: lambda p: p.get('total_size_bytes', 0)
        }
        
        sort_key = sort_key_map.get(sort_by, sort_key_map[SortBy.NAME])
        return sorted(packages, key=sort_key, reverse=reverse)
    
    def format_packages_json(self, packages: List[Dict[str, Any]]) -> str:
        """Format packages as JSON."""
        return json.dumps(packages, indent=2, default=str)
    
    def format_packages_csv(self, packages: List[Dict[str, Any]]) -> str:
        """Format packages as CSV."""
        if not packages:
            return "No packages found"
        
        import csv
        import io
        
        output = io.StringIO()
        fieldnames = [
            'name', 'version', 'package_type', 'project_name', 'project_path',
            'created_at', 'total_size_mb', 'file_count', 'status', 'package_url', 'package_files_url', 'project_registry_url'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for package in packages:
            row = {field: package.get(field, '') for field in fieldnames}
            writer.writerow(row)
        
        return output.getvalue()
    
    def format_packages_table(self, packages: List[Dict[str, Any]]) -> str:
        """Format packages as a readable table."""
        if not packages:
            return "No packages found"
        
        # Calculate column widths
        headers = ['Name', 'Version', 'Type', 'Project', 'Size (MB)', 'Files', 'Created', 'Package URL']
        col_widths = [len(h) for h in headers]
        
        rows = []
        for package in packages:
            # Truncate URL for display
            package_url = package.get('package_url', '')
            display_url = package_url[:50] + '...' if len(package_url) > 50 else package_url
            
            row = [
                package.get('name', '')[:30],
                package.get('version', '')[:15],
                package.get('package_type', '')[:10],
                package.get('project_name', '')[:20],
                str(package.get('total_size_mb', 0)),
                str(package.get('file_count', 0)),
                package.get('created_at', '')[:10] if package.get('created_at') else '',
                display_url
            ]
            rows.append(row)
            
            # Update column widths
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Build table
        separator = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
        header_row = '|' + '|'.join(f' {h:<{col_widths[i]}} ' for i, h in enumerate(headers)) + '|'
        
        result = [separator, header_row, separator]
        
        for row in rows:
            data_row = '|' + '|'.join(f' {str(cell):<{col_widths[i]}} ' for i, cell in enumerate(row)) + '|'
            result.append(data_row)
        
        result.append(separator)
        return '\n'.join(result)
    
    def format_packages_summary(self, packages: List[Dict[str, Any]]) -> str:
        """Format packages as a summary report."""
        if not packages:
            return "No packages found"
        
        # Count by type
        type_counts = {}
        project_counts = {}
        total_size = 0
        
        for package in packages:
            pkg_type = package.get('package_type', 'unknown')
            project = package.get('project_name', 'unknown')
            size = package.get('total_size_bytes', 0)
            
            type_counts[pkg_type] = type_counts.get(pkg_type, 0) + 1
            project_counts[project] = project_counts.get(project, 0) + 1
            total_size += size
        
        result = [
            "GitLab Package Registry Summary",
            "=" * 40,
            f"Total packages: {len(packages)}",
            f"Total size: {round(total_size / (1024 * 1024), 2)} MB",
            "",
            "Packages by type:",
        ]
        
        for pkg_type, count in sorted(type_counts.items()):
            result.append(f"  {pkg_type}: {count}")
        
        result.extend([
            "",
            "Top projects by package count:",
        ])
        
        top_projects = sorted(project_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for project, count in top_projects:
            result.append(f"  {project}: {count}")
        
        return '\n'.join(result)
    
    def save_output(self, content: str, filename: str, output_dir: str, packages: List[Dict[str, Any]] = None):
        """Save output to file with metadata."""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Create a summary metadata file
        if packages is not None:
            self._create_summary_file(output_dir, packages, filename)
        
        if self.verbose:
            print(f"Output saved to: {filepath}")
        
        return filepath
    
    def _create_summary_file(self, output_dir: str, packages: List[Dict[str, Any]], main_filename: str):
        """Create a summary file with metadata about the export."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Count by type
        type_counts = {}
        project_counts = {}
        total_size = 0
        
        for package in packages:
            pkg_type = package.get('package_type', 'unknown')
            project = package.get('project_name', 'unknown')
            size = package.get('total_size_bytes', 0)
            
            type_counts[pkg_type] = type_counts.get(pkg_type, 0) + 1
            project_counts[project] = project_counts.get(project, 0) + 1
            total_size += size
        
        summary_content = [
            f"GitLab Package Registry Export Summary",
            f"Generated: {timestamp}",
            f"GitLab Instance: {self.config.gitlab_url}",
            f"Main Export File: {main_filename}",
            "=" * 60,
            "",
            f"Total packages exported: {len(packages)}",
            f"Total size: {round(total_size / (1024 * 1024), 2)} MB",
            "",
            "Packages by type:",
        ]
        
        for pkg_type, count in sorted(type_counts.items()):
            summary_content.append(f"  {pkg_type}: {count}")
        
        summary_content.extend([
            "",
            "Top projects by package count:",
        ])
        
        top_projects = sorted(project_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for project, count in top_projects:
            summary_content.append(f"  {project}: {count}")
        
        summary_content.extend([
            "",
            "Export Parameters:",
            f"  Format: {main_filename.split('.')[-1] if '.' in main_filename else 'table'}",
            f"  Timestamp: {timestamp}",
            f"  Output directory: {output_dir}",
        ])
        
        summary_path = os.path.join(output_dir, f"export_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_content))
        
        if self.verbose:
            print(f"Summary saved to: {summary_path}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='List packages and libraries in GitLab Package Registry'
    )
    
    parser.add_argument(
        '--type',
        type=str,
        choices=[pt.value for pt in PackageType],
        help='Filter by package type'
    )
    
    parser.add_argument(
        '--project-ids',
        type=str,
        nargs='+',
        help='Specific project IDs to check (default: all projects)'
    )
    
    parser.add_argument(
        '--search',
        type=str,
        help='Search term to filter packages by name, project, or version'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=[of.value for of in OutputFormat],
        default=OutputFormat.TABLE.value,
        help='Output format (default: table)'
    )
    
    parser.add_argument(
        '--sort-by',
        type=str,
        choices=[sb.value for sb in SortBy],
        default=SortBy.NAME.value,
        help='Sort packages by field (default: name)'
    )
    
    parser.add_argument(
        '--reverse',
        action='store_true',
        help='Reverse sort order'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for files (default: timestamped directory)'
    )
    
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save output to file'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output for troubleshooting'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Include detailed package information (slower)'
    )
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()
    
    try:
        # Initialize lister
        lister = GitLabRegistryLister(verbose=args.verbose, debug=args.debug)
        
        # Parse package type filter
        package_type = None
        if args.type:
            package_type = PackageType(args.type)
        
        # Get packages
        if args.verbose:
            print("Fetching packages from GitLab registry...")
        
        packages = lister.get_all_packages(
            package_type=package_type,
            project_ids=args.project_ids
        )
        
        if args.verbose:
            print(f"Found {len(packages)} packages")
        
        # Enhance with detailed information if requested or if saving (URLs are needed)
        if args.detailed or args.save:
            if args.verbose:
                print("Enhancing with detailed package information...")
            packages = lister.enhance_package_data(packages)
        
        # Filter packages
        if args.search:
            packages = lister.filter_packages(packages, search_term=args.search)
            if args.verbose:
                print(f"Filtered to {len(packages)} packages matching '{args.search}'")
        
        # Sort packages
        sort_by = SortBy(args.sort_by)
        packages = lister.sort_packages(packages, sort_by, args.reverse)
        
        # Format output
        output_format = OutputFormat(args.format)
        
        if output_format == OutputFormat.JSON:
            output = lister.format_packages_json(packages)
            filename = "packages.json"
        elif output_format == OutputFormat.CSV:
            output = lister.format_packages_csv(packages)
            filename = "packages.csv"
        elif output_format == OutputFormat.SUMMARY:
            output = lister.format_packages_summary(packages)
            filename = "packages_summary.txt"
        else:  # TABLE
            output = lister.format_packages_table(packages)
            filename = "packages_table.txt"
        
        # Output results
        print(output)
        
        # Save to file if requested
        if args.save:
            output_dir = args.output_dir or create_packages_report_directory()
            saved_file = lister.save_output(output, filename, output_dir, packages)
            print(f"\nOutput saved to: {saved_file}")
            print(f"Report directory: {output_dir}")
    
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 