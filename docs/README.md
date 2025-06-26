# GitLab Analysis Tool Documentation

Welcome to the comprehensive documentation for the GitLab Analysis Tool - a powerful Python toolkit for analyzing GitLab repositories, managing issues, and exploring package registries.

## 📚 Available Documentation

### 🛠️ Core Tools Documentation

#### 📦 [GitLab Package Registry Lister](gitlab_registry_packages.md)
**Complete guide to analyzing GitLab Package Registries**
- Multi-registry support (NPM, Maven, Helm, PyPI, NuGet, Docker, etc.)
- Direct package URLs for code access
- Advanced filtering and search capabilities
- Multiple output formats (Table, JSON, CSV, Summary)
- Usage examples and troubleshooting

#### 🎫 [GitLab to Jira Export](gitlab_jira_export.md)  
**Comprehensive guide for exporting GitLab issues to Jira**
- Issue export formatting and field mapping
- User context preservation
- Priority and component detection
- Jira import procedures and best practices

### 🤝 Development & Contributing

#### [Contributing Guidelines](CONTRIBUTING.md)
**How to contribute to the project**
- Code standards and TypeScript-strict patterns
- Enum usage requirements
- Testing requirements and procedures
- Development workflow

## 🎯 Script Reference

### Main Entry Point
```bash
python gitlab_analysis.py [command] [options]
```

**Available Commands:**
- `analyze` - Repository commit analysis
- `export-markdown` - Issue export in Markdown format
- `export-csv` - Issue export in CSV format  
- `export-jira` - Issue export for Jira import
- `list-packages` - Package registry analysis
- `check-access` - GitLab access verification

### Individual Scripts

#### 📊 Repository Analysis
```bash
python scripts/analyze_local_repos.py --days 30 --verbose
```
- Comprehensive commit analysis across all branches
- Author statistics with email consolidation
- Activity patterns and timeline analysis
- Offline and online analysis modes

#### 📋 Issue Export Tools
```bash
# Markdown export
python scripts/export_recent_issues.py --days 7

# CSV export  
python scripts/export_recent_issues_csv.py --days 14

# Jira-compatible export
python scripts/export_issues_for_jira.py --days 60 --verbose
```
- Smart filtering by creation/update date
- Full context preservation (descriptions, assignees, labels)
- User information and cross-references
- Multiple export formats

#### 📦 Package Registry Management
```bash
python scripts/list_registry_packages.py --type npm --format csv --save
```
- All GitLab package registries (NPM, Maven, Helm, etc.)
- Direct URLs to package source code
- Advanced filtering and search
- Export with comprehensive metadata

#### 🔧 Utility Scripts
```bash
python scripts/check_project_access.py
```
- GitLab connectivity verification
- Permission and access testing
- Token validation

## 📊 Output Structure Reference

### Repository Analysis Outputs
```
gitlab_reports/analysis_YYYYMMDD_HHMMSS/
├── analysis_report_YYYYMMDD_HHMMSS.txt    # Detailed text report
├── analysis_data_YYYYMMDD_HHMMSS.csv      # Structured CSV data
├── repository_index_YYYYMMDD_HHMMSS.json  # Repository metadata
└── individual_repo_reports/                # Per-repository files
```

### Issue Export Outputs
```
gitlab_reports/
├── issues_export_YYYYMMDD_HHMMSS/          # Markdown format
├── issues_csv_YYYYMMDD_HHMMSS/             # CSV format
└── jira_YYYYMMDD_HHMMSS/                   # Jira import format
```

### Package Registry Outputs  
```
gitlab_packages_report/packages_report_YYYYMMDD_HHMMSS/
├── packages.csv                            # Complete listing with URLs
├── packages_summary.txt                    # Statistics
└── export_summary_YYYYMMDD_HHMMSS.txt     # Export metadata
```

## 🚀 Quick Start Examples

### Repository Analysis
```bash
# Analyze last 30 days with detailed output
python gitlab_analysis.py analyze --days 30

# Verbose repository analysis with local cloning
python scripts/analyze_local_repos.py --days 60 --verbose
```

### Issue Management
```bash
# Export recent issues for Jira import
python gitlab_analysis.py export-jira --days 60

# CSV export for spreadsheet analysis
python gitlab_analysis.py export-csv --days 14
```

### Package Registry
```bash
# List all NPM packages with URLs
python gitlab_analysis.py list-packages --type npm --save

# Search for specific packages
python scripts/list_registry_packages.py --search "cp-" --detailed
```

## 🔍 Troubleshooting Quick Reference

### Common Solutions
| Problem | Quick Fix |
|---------|-----------|
| **Token not found** | Check `.env` file exists with `GITLAB_TOKEN` |
| **403 Forbidden** | Verify token scopes: `api`, `read_repository`, `read_registry` |
| **Empty package URLs** | Use `--save` or `--detailed` flag |
| **No repositories found** | Check token permissions and GitLab URL |

### Debug Commands
```bash
# Test GitLab connection
python scripts/check_project_access.py

# Debug package registry access
python scripts/list_registry_packages.py --debug

# Verbose repository analysis
python scripts/analyze_local_repos.py --verbose --list-only
```

## 📖 Advanced Topics

### Configuration Management
- Environment variables and `.env` setup
- Advanced configuration options
- Custom SSH configurations for repository cloning

### Integration Workflows
- CI/CD pipeline integration
- Automated reporting schedules
- Custom data processing pipelines

### API Usage Patterns
- GitLab API rate limiting and optimization
- Bulk operations and pagination handling
- Error handling and retry strategies

## 🔗 External Resources

### GitLab API Documentation
- [GitLab API Reference](https://docs.gitlab.com/ee/api/)
- [Package Registry API](https://docs.gitlab.com/ee/api/packages.html)
- [Issues API](https://docs.gitlab.com/ee/api/issues.html)

### Related Tools
- [GitLab Runner](https://docs.gitlab.com/runner/) - CI/CD automation
- [GitLab CLI](https://gitlab.com/gitlab-org/cli) - Command-line interface
- [python-gitlab](https://python-gitlab.readthedocs.io/) - Python SDK

---

**Need more help?** Check the main [README.md](../README.md) for comprehensive setup instructions and feature overview. 