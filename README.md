# GitLab Analysis Tool

A comprehensive Python toolkit for analyzing GitLab repositories, exporting issues, and managing package registries. This tool provides detailed commit analysis, flexible issue export capabilities, and comprehensive package registry management.

## 🚀 Features

### 📊 Repository Analysis
- **Comprehensive Commit Analysis**: Activity patterns, author statistics, and timeline analysis
- **Email Consolidation**: Automatic grouping of commits by author email
- **Branch-Aware**: Analyzes all branches, not just the default branch
- **Offline Mode**: Enhanced support for analyzing local repositories
- **Merge Commit Filtering**: Excludes merge commits for accurate statistics

### 📋 Issue Export & Management
- **Multiple Export Formats**: Markdown, CSV, and Jira-compatible formats
- **Smart Filtering**: Export issues by date range and activity
- **User Context Preservation**: Maintains author and assignee information
- **Jira Integration**: Pre-formatted CSV files ready for Jira import
- **Consolidated Reports**: Combine issues from multiple projects

### 📦 Package Registry Analysis
- **Multi-Registry Support**: NPM, Maven, Helm, PyPI, NuGet, Docker, and more
- **Direct Package Links**: URLs to view package code and files
- **Comprehensive Metadata**: Package sizes, file counts, creation dates
- **Advanced Filtering**: By package type, search terms, and project scope
- **Multiple Output Formats**: Table, JSON, CSV, and summary views

### 🔧 Utility Tools
- **Project Access Verification**: Check GitLab permissions and connectivity
- **Environment Configuration**: Streamlined setup and troubleshooting
- **Debug Support**: Comprehensive logging and error handling

## 📁 Project Structure

```
gitlab-analysis/
├── gitlab_analysis.py                    # 🎯 Main unified entry point
├── scripts/                              # 🛠️ Individual tool scripts
│   ├── analyze_local_repos.py            #   📊 Repository analysis
│   ├── export_recent_issues.py           #   📄 Markdown issue export
│   ├── export_recent_issues_csv.py       #   📊 CSV issue export
│   ├── export_issues_for_jira.py         #   🎫 Jira import format
│   ├── list_registry_packages.py         #   📦 Package registry analysis
│   └── check_project_access.py           #   🔒 Access verification
├── src/                                  # 📚 Shared utilities
│   ├── __init__.py
│   └── gitlab_utils.py                   #   🔧 Common GitLab utilities
├── config/                               # ⚙️ Configuration files
│   ├── env.template                      #   📝 Environment template
│   ├── settings.py                       #   ⚙️ Configuration management
│   └── README.md                         #   📖 Config documentation
├── docs/                                 # 📖 Documentation
│   ├── README.md                         #   📚 Documentation index
│   ├── CONTRIBUTING.md                   #   🤝 Contribution guidelines
│   ├── gitlab_jira_export.md            #   🎫 Jira export guide
│   └── gitlab_registry_packages.md      #   📦 Package registry guide
├── gitlab_reports/                       # 📊 Analysis & issue export outputs
│   ├── analysis_YYYYMMDD_HHMMSS/        #   📈 Repository analysis
│   ├── issues_export_YYYYMMDD_HHMMSS/   #   📄 Markdown exports
│   ├── issues_csv_YYYYMMDD_HHMMSS/      #   📊 CSV exports
│   └── jira_YYYYMMDD_HHMMSS/            #   🎫 Jira import files
├── gitlab_packages_report/               # 📦 Package registry outputs
│   └── packages_report_YYYYMMDD_HHMMSS/ #   📦 Package listings & metadata
├── projects/                             # 📂 Cloned GitLab repositories
├── requirements.txt                      # 📋 Python dependencies
└── .env                                 # 🔐 Environment configuration
```

## 🛠️ Setup

### Prerequisites
- **Python 3.8+**
- **Git**
- **GitLab Personal Access Token**

### Quick Setup

1. **Clone & Setup Environment**
   ```bash
   git clone <your-repo-url>
   cd gitlab-analysis
   
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure GitLab Access**
   ```bash
   # Copy configuration template
   cp config/env.template .env
   
   # Edit .env with your GitLab credentials
   # Required: GITLAB_URL and GITLAB_TOKEN
   ```

3. **Generate GitLab Personal Access Token**
   - Go to: **GitLab → Profile → Access Tokens → Personal Access Tokens**
   - **Required scopes**: `api`, `read_repository`, `read_registry`
   - Copy token to `.env` file

4. **Verify Setup**
   ```bash
   # Test GitLab connection
   python gitlab_analysis.py check-access
   ```

## 🎯 Usage

### Unified Interface (Recommended)

The main entry point provides a unified interface for all tools:

```bash
# Show all available commands
python gitlab_analysis.py --help

# Repository Analysis
python gitlab_analysis.py analyze --days 30

# Issue Export
python gitlab_analysis.py export-markdown --days 7
python gitlab_analysis.py export-csv --days 14
python gitlab_analysis.py export-jira --days 60

# Package Registry
python gitlab_analysis.py list-packages --type npm --save
python gitlab_analysis.py list-packages --format csv --save

# Utility Commands
python gitlab_analysis.py check-access
```

### Direct Script Usage

For advanced usage, run scripts directly:

```bash
# Repository Analysis
python scripts/analyze_local_repos.py --days 30 --verbose

# Issue Exports
python scripts/export_recent_issues.py --days 7
python scripts/export_recent_issues_csv.py --days 14 
python scripts/export_issues_for_jira.py --days 60

# Package Registry Management
python scripts/list_registry_packages.py --type npm --format csv --save
python scripts/list_registry_packages.py --search "cp-" --detailed

# Utilities
python scripts/check_project_access.py
```

## 📊 Output Structure

### Repository Analysis (`gitlab_reports/analysis_YYYYMMDD_HHMMSS/`)
```
analysis_report_YYYYMMDD_HHMMSS.txt    # Detailed analysis report
analysis_data_YYYYMMDD_HHMMSS.csv      # Structured data for spreadsheets
repository_index_YYYYMMDD_HHMMSS.json  # Repository metadata
individual_repo_reports/                # Per-repository analysis files
```

### Issue Exports (`gitlab_reports/`)
```
issues_export_YYYYMMDD_HHMMSS/          # Markdown format
├── ProjectName_issues_YYYYMMDD.md
└── issues_summary_YYYYMMDD.md

issues_csv_YYYYMMDD_HHMMSS/             # CSV format
├── ProjectName_issues_YYYYMMDD.csv
├── all_issues_consolidated_YYYYMMDD.csv
└── csv_export_summary_YYYYMMDD.txt

jira_YYYYMMDD_HHMMSS/                   # Jira import format
├── ProjectName_jira_import_YYYYMMDD.csv
├── all_issues_jira_import_YYYYMMDD.csv
└── jira_import_summary_YYYYMMDD.txt
```

### Package Registry (`gitlab_packages_report/packages_report_YYYYMMDD_HHMMSS/`)
```
packages.csv                            # Complete package listing with URLs
packages_summary.txt                    # Summary statistics
export_summary_YYYYMMDD_HHMMSS.txt     # Export metadata and parameters
```

## 🔧 Advanced Features

### Repository Analysis
- **Smart Author Detection**: Consolidates commits by email across multiple names
- **Activity Heatmaps**: Identifies peak development periods and patterns
- **File Change Tracking**: Most modified files and directory analysis
- **Branch Coverage**: Analyzes activity across all branches simultaneously
- **Offline Capability**: Full analysis of locally cloned repositories

### Issue Management
- **Intelligent Filtering**: Recent activity detection (created/updated in timeframe)
- **Rich Context**: Includes descriptions, comments, assignees, labels, milestones
- **Cross-Reference Preservation**: Maintains links to original GitLab issues
- **User Information**: Full author and assignee details for accountability

### Package Registry Features
- **Direct Code Access**: URLs to view package source code and files
- **Comprehensive Metadata**: Package sizes, file counts, creation dates, versions
- **Multi-Registry Support**: NPM, Maven, PyPI, Helm, NuGet, Docker, and more
- **Advanced Search**: Filter by name, project, version, or package type
- **Export Flexibility**: Table, JSON, CSV, and summary formats

### Jira Integration
- **Smart Field Mapping**: Automatic GitLab to Jira field conversion
- **Priority Intelligence**: Label-based priority assignment
- **Component Detection**: Extract components from labels and repository names
- **User Context**: Rich user information preserved in descriptions

## 🔍 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **"GitLab private token not found"** | Ensure `.env` file exists with valid `GITLAB_TOKEN` |
| **"403 Forbidden" errors** | Verify token has required scopes: `api`, `read_repository`, `read_registry` |
| **"Projects directory not found"** | Create `projects/` directory or use online mode for auto-cloning |
| **"Could not access GitLab project"** | Check repository URLs and token permissions |
| **Package URLs empty** | Use `--save` or `--detailed` flag to enable URL generation |

### Debug Mode

Enable detailed logging for any script:

```bash
# Repository analysis with verbose output
python scripts/analyze_local_repos.py --verbose --days 30

# Package registry with debug information  
python scripts/list_registry_packages.py --debug --verbose

# Issue export with detailed progress
python scripts/export_issues_for_jira.py --verbose --days 60
```

### Environment Verification

```bash
# Check GitLab connectivity
python scripts/check_project_access.py

# Verify token permissions
python scripts/list_registry_packages.py --debug

# Test repository access
python scripts/analyze_local_repos.py --list-only --verbose
```

## 📖 Documentation

### Quick References
- **[Package Registry Guide](docs/gitlab_registry_packages.md)** - Complete package management documentation
- **[Jira Export Guide](docs/gitlab_jira_export.md)** - Detailed Jira integration instructions
- **[Configuration Guide](config/README.md)** - Advanced configuration options
- **[Contributing Guide](docs/CONTRIBUTING.md)** - Development and contribution guidelines

### Script-Specific Documentation
Each script includes built-in help:
```bash
python scripts/analyze_local_repos.py --help
python scripts/list_registry_packages.py --help
python scripts/export_issues_for_jira.py --help
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Follow** TypeScript-strict patterns and enum usage
4. **Test** your changes thoroughly
5. **Commit** with descriptive messages
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License.

## 🚀 Version History

- **v1.2.0** - Enhanced Package Registry with direct code URLs
  - Package URL generation for easy code access
  - Improved error handling and Windows compatibility
  - Enhanced documentation and unified interface
  
- **v1.1.0** - Comprehensive Package Registry Analysis
  - Multi-registry support (NPM, Maven, Helm, PyPI, etc.)
  - Advanced filtering and search capabilities
  - Multiple export formats with metadata

- **v1.0.0** - Initial release with organized structure
  - Unified entry point and organized folder structure
  - Comprehensive repository analysis and issue export
  - Timestamped output directories and documentation

## 💬 Support

**Need Help?**

1. **Check Documentation**: Review the troubleshooting section and script-specific docs
2. **Search Issues**: Look through existing GitHub issues
3. **Create New Issue**: Include problem description, steps to reproduce, error messages, and environment details

---

**Happy Analyzing! 🚀📊📦**
