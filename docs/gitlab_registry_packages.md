# GitLab Registry Package Lister

A comprehensive tool for listing and analyzing packages in GitLab Package Registry. This script supports all GitLab package types including NPM, Maven, Helm, PyPI, and more.

## Overview

The GitLab Registry Package Lister (`list_registry_packages.py`) provides a unified interface to explore and analyze packages stored in your GitLab Package Registry. It supports multiple output formats, filtering options, and detailed package information.

### Supported Package Types

- **NPM** - JavaScript/Node.js packages (like npm.js registry)
- **Maven** - Java packages and dependencies  
- **PyPI** - Python packages
- **NuGet** - .NET packages
- **Composer** - PHP packages
- **Helm** - Kubernetes deployment charts
- **Generic** - Custom package format
- **Conan** - C/C++ packages
- **Terraform** - Infrastructure modules
- **Debian/RPM** - Linux packages
- **RubyGems** - Ruby packages

## Installation & Setup

### Prerequisites

1. **Python Environment**: Ensure Python 3.8+ is installed
2. **Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **GitLab Access Token**: Generate a Personal Access Token with these scopes:
   - `api` (required for package registry access)
   - `read_repository` (required for project access) 
   - `read_registry` (specifically for package registry)

### Configuration

1. **Environment Variables**: Set up your GitLab connection:
   ```bash
   export GITLAB_URL=https://your-gitlab-instance.com
   export GITLAB_TOKEN=your_personal_access_token
   ```

2. **Or use .env file**: Copy and configure the environment template:
   ```bash
   cp config/env.template .env
   # Edit .env and set your GITLAB_TOKEN
   ```

## Usage

### Basic Usage

```bash
# List all packages in table format (default)
python scripts/list_registry_packages.py

# List with verbose output to see progress
python scripts/list_registry_packages.py --verbose
```

### Package Type Filtering

```bash
# Show only NPM packages (your npm.js-like registry)
python scripts/list_registry_packages.py --type npm

# Show only Maven packages
python scripts/list_registry_packages.py --type maven

# Show only Helm charts
python scripts/list_registry_packages.py --type helm
```

### Search and Filtering

```bash
# Search for packages containing "tracking"
python scripts/list_registry_packages.py --search "tracking"

# Search for specific project packages
python scripts/list_registry_packages.py --search "cp-api"

# Filter by specific project IDs
python scripts/list_registry_packages.py --project-ids 123 456 789
```

### Output Formats

```bash
# Table format (default) - human-readable
python scripts/list_registry_packages.py --format table

# JSON format - machine-readable
python scripts/list_registry_packages.py --format json

# CSV format - spreadsheet-compatible
python scripts/list_registry_packages.py --format csv

# Summary format - statistics and overview
python scripts/list_registry_packages.py --format summary
```

### Sorting Options

```bash
# Sort by package name (default)
python scripts/list_registry_packages.py --sort-by name

# Sort by creation date (newest first)
python scripts/list_registry_packages.py --sort-by created --reverse

# Sort by package size (largest first)
python scripts/list_registry_packages.py --sort-by size --reverse --detailed

# Sort by project name
python scripts/list_registry_packages.py --sort-by project
```

### File Output

```bash
# Save output to timestamped directory
python scripts/list_registry_packages.py --save

# Save to custom directory
python scripts/list_registry_packages.py --save --output-dir my-packages-report

# Export CSV for spreadsheet analysis
python scripts/list_registry_packages.py --format csv --save
```

### Detailed Information

```bash
# Include detailed package information (file counts, sizes)
python scripts/list_registry_packages.py --detailed

# Combine with other options
python scripts/list_registry_packages.py --detailed --sort-by size --reverse --save
```

## Command-Line Reference

### Required Arguments
None - all arguments are optional with sensible defaults.

### Optional Arguments

| Argument | Type | Description | Example |
|----------|------|-------------|---------|
| `--type` | string | Filter by package type | `--type npm` |
| `--project-ids` | list | Specific project IDs to check | `--project-ids 123 456` |
| `--search` | string | Search term for filtering | `--search "tracking"` |
| `--format` | string | Output format | `--format json` |
| `--sort-by` | string | Sort packages by field | `--sort-by created` |
| `--reverse` | flag | Reverse sort order | `--reverse` |
| `--output-dir` | string | Custom output directory | `--output-dir reports` |
| `--save` | flag | Save output to file | `--save` |
| `--verbose` | flag | Enable verbose output | `--verbose` |
| `--detailed` | flag | Include detailed package info | `--detailed` |

### Package Types
`npm`, `pypi`, `maven`, `nuget`, `composer`, `generic`, `conan`, `helm`, `terraform`, `debian`, `rpm`, `rubygems`

### Output Formats  
`table`, `json`, `csv`, `summary`

### Sort Options
`name`, `type`, `project`, `version`, `created`, `size`

## Examples

### Example 1: NPM Registry Analysis
```bash
# Analyze your NPM packages (like npm.js registry)
python scripts/list_registry_packages.py --type npm --format summary --verbose

# Export NPM packages to CSV
python scripts/list_registry_packages.py --type npm --format csv --save

# Find all tracking-related NPM packages
python scripts/list_registry_packages.py --type npm --search "tracking" --detailed
```

### Example 2: Package Size Analysis
```bash
# Find largest packages across all types
python scripts/list_registry_packages.py --detailed --sort-by size --reverse

# Export size analysis to JSON
python scripts/list_registry_packages.py --detailed --sort-by size --format json --save
```

### Example 3: Recent Package Activity
```bash
# Show recently created packages
python scripts/list_registry_packages.py --sort-by created --reverse

# Show recent NPM packages only
python scripts/list_registry_packages.py --type npm --sort-by created --reverse
```

### Example 4: Project-Specific Analysis
```bash
# Analyze packages from specific projects
python scripts/list_registry_packages.py --project-ids 274 272 271 --detailed

# Export project-specific packages
python scripts/list_registry_packages.py --project-ids 274 272 --format csv --save
```

## Output Examples

### Table Format
```
+--------------------------------+---------+-------+---------+-----------+-------+------------+
| Name                           | Version | Type  | Project | Size (MB) | Files | Created    |
+--------------------------------+---------+-------+---------+-----------+-------+------------+
| @libraries/cp-accounting       | 0.0.4   | npm   |         | 0         | 0     | 2024-09-04 |
| @libraries/cp-api-shared       | 0.0.21  | npm   |         | 0         | 0     | 2024-06-04 |
| @libraries/cp-dates            | 0.0.7   | npm   |         | 0         | 0     | 2025-02-03 |
+--------------------------------+---------+-------+---------+-----------+-------+------------+
```

### Summary Format
```
GitLab Package Registry Summary
========================================
Total packages: 396
Total size: 15.4 MB

Packages by type:
  npm: 323
  maven: 61
  helm: 12

Top projects by package count:
  Customer Portal Libraries: 156
  Infrastructure Tools: 89
  API Components: 67
```

### JSON Format
```json
[
  {
    "name": "@libraries/cp-accounting",
    "version": "0.0.4",
    "package_type": "npm",
    "created_at": "2024-09-04T10:30:00.000Z",
    "project_id": 274,
    "project_name": "Customer Portal Libraries",
    "total_size_bytes": 2048,
    "file_count": 15
  }
]
```

## Understanding Your Registry

Based on analysis of a typical GitLab registry, you might see:

### Package Organization
- **@libraries/** scope - Internal shared libraries
- **@components/** scope - Reusable UI components  
- **@tools/** scope - Development and build tools
- **@api/** scope - API-specific packages

### Common Package Patterns
- **Versioning**: Semantic versioning (0.0.1, 0.0.2, etc.)
- **Naming**: Prefixed with organization scope
- **Types**: Mix of NPM (frontend), Maven (backend), Helm (deployment)

## Troubleshooting

### Authentication Issues

**Problem**: `401: invalid_token` error
```bash
Error: 401: invalid_token
```

**Solutions**:
1. Check if token is set: `echo $GITLAB_TOKEN`
2. Verify token hasn't expired
3. Ensure token has required scopes: `api`, `read_repository`, `read_registry`
4. Regenerate token if needed

**Problem**: `403: Forbidden` for some projects
```bash
Error fetching packages for project 123: 403 Client Error: Forbidden
```

**Solutions**:
1. Normal behavior - you don't have access to all projects
2. Use `--project-ids` to specify only accessible projects
3. Contact project owners for access if needed

### Connection Issues

**Problem**: Cannot connect to GitLab instance
```bash
Error: Connection timeout
```

**Solutions**:
1. Verify `GITLAB_URL` is correct
2. Check network connectivity
3. Ensure GitLab instance is accessible
4. Try with `--verbose` for more details

### Performance Issues

**Problem**: Script runs slowly
```bash
Found 1000+ projects to check...
```

**Solutions**:
1. Use `--project-ids` to limit scope
2. Avoid `--detailed` for large registries
3. Filter by `--type` to reduce processing
4. Use `--verbose` to monitor progress

### No Packages Found

**Problem**: Script shows 0 packages
```bash
No packages found
```

**Solutions**:
1. Verify you have access to projects with packages
2. Check if Package Registry is enabled on GitLab instance
3. Try specific `--project-ids` you know have packages
4. Use `--verbose` to see what's happening

## Integration with Other Tools

### With Jira Export
```bash
# Combine with issue analysis
python scripts/export_issues_for_jira.py --verbose
python scripts/list_registry_packages.py --save --format csv
```

### With CI/CD Pipelines
```bash
# Daily package registry report
python scripts/list_registry_packages.py \
  --format json \
  --save \
  --output-dir daily-reports \
  --verbose
```

### With Monitoring Systems
```bash
# Export for monitoring dashboards
python scripts/list_registry_packages.py \
  --format json \
  --detailed \
  > /monitoring/gitlab-packages.json
```

## API Reference

The script uses GitLab Package Registry API endpoints:

- `GET /api/v4/projects/:id/packages` - List project packages
- `GET /api/v4/projects/:id/packages/:package_id` - Package details  
- `GET /api/v4/projects/:id/packages/:package_id/package_files` - Package files

### Required Permissions
- **API Access**: `api` scope on Personal Access Token
- **Repository Access**: `read_repository` scope
- **Registry Access**: `read_registry` scope

## Best Practices

### Regular Monitoring
```bash
# Weekly package summary
python scripts/list_registry_packages.py --format summary --save

# Monthly detailed export  
python scripts/list_registry_packages.py --detailed --format csv --save
```

### Security Considerations
1. Keep access tokens secure and rotate regularly
2. Use minimal required scopes
3. Monitor package access patterns
4. Regular audit of package contents

### Performance Optimization
1. Use filtering options to reduce API calls
2. Save results for repeated analysis
3. Use `--project-ids` for targeted analysis
4. Avoid `--detailed` for regular monitoring

## Contributing

This script is part of the GitLab Analysis Tool suite. For contributions:

1. Follow the existing code patterns
2. Use TypeScript-strict typing with enums
3. Add comprehensive error handling
4. Update documentation for new features
5. Test with various GitLab configurations

## Version History

- **v1.0**: Initial release with basic package listing
- **v1.1**: Added multiple output formats and filtering
- **v1.2**: Enhanced with detailed package information
- **v1.3**: Added sorting and search capabilities

For the latest updates, check the git history of `scripts/list_registry_packages.py`. 