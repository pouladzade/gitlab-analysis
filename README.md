# GitLab Analysis ToolA comprehensive Python tool for analyzing GitLab repositories and exporting issues in various formats. This tool provides detailed commit analysis, author statistics, and flexible issue export capabilities.**Repository:** [https://github.com/pouladzade/gitlab-analysis](https://github.com/pouladzade/gitlab-analysis)

## Features

### Repository Analysis

- **Commit Analysis**: Detailed commit frequency and activity patterns
- **Author Statistics**: Email consolidation and contributor insights
- **Activity Metrics**: Timeline analysis and productivity metrics
- **Comprehensive Reports**: Both text and CSV output formats

### Issue Export

- **Markdown Export**: Human-readable issue reports with full context
- **CSV Export**: Structured data for spreadsheet analysis
- **Jira Import**: Pre-formatted CSV files ready for Jira import with user context

## Project Structure

```gitlab-analysis/
├── scripts/                              # Main executable scripts│   ├── analyze_local_repos.py            # Repository analysis│   ├── export_recent_issues.py           # Markdown issue export│   ├── export_recent_issues_csv.py       # CSV issue export│   └── export_issues_for_jira.py         # Jira import format
├── src/                                  # Shared utilities
│   ├── __init__.py                       # Package initialization
│   └── gitlab_utils.py                   # Common GitLab utilities
├── config/                               # Configuration files
├── docs/                                 # Documentation
├── archive/                              # Legacy scripts
├── gitlab_reports/                       # Generated reports (timestamped folders)
│   ├── analysis_YYYYMMDD_HHMMSS/        # Analysis outputs
│   ├── issues_export_YYYYMMDD_HHMMSS/   # Markdown exports
│   ├── issues_csv_YYYYMMDD_HHMMSS/      # CSV exports
│   └── jira_YYYYMMDD_HHMMSS/            # Jira import files
├── projects/                             # Cloned GitLab repositories
├── gitlab_analysis.py                    # Main entry point
├── requirements.txt                      # Python dependencies
└── README.md                            # This file
```

## Setup

### Prerequisites

- Python 3.8 or higher
- Git
- GitLab Personal Access Token

### Installation

1. **Clone the repository** `bash   git clone git@github.com:pouladzade/gitlab-analysis.git   cd gitlab-analysis   `

2. **Create virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure GitLab access** `bash   # Copy configuration template   cp config/env.template .env      # Edit .env file with your GitLab credentials   # Set GITLAB_URL and GITLAB_TOKEN   `

   **To generate a GitLab Personal Access Token:**

   - Go to GitLab → Profile → Access Tokens → Personal Access Tokens
   - Required scopes: `api`, `read_repository`

5. **Clone your repositories**

   ```bash
   # Create projects directory
   mkdir -p projects

   # Clone your GitLab repositories into projects/
   cd projects
   git clone git@gitlab.example.com:group/repo1.git
   git clone git@gitlab.example.com:group/repo2.git
   # ... add more repositories
   ```

## Usage

### Main Entry Point (Recommended)

Use the unified interface for all operations:

```bash
# Show help and available commands
python gitlab_analysis.py --help

# Analyze repositories (last 30 days)
python gitlab_analysis.py analyze --days 30

# Export issues as Markdown
python gitlab_analysis.py export-markdown --days 7

# Export issues as CSV
python gitlab_analysis.py export-csv --days 14

# Export for Jira import
python gitlab_analysis.py export-jira --days 60
```

### Direct Script Usage

You can also run scripts directly:

```bash
# Repository analysispython scripts/analyze_local_repos.py --days 30

# Issue exports
python scripts/export_recent_issues.py --days 7
python scripts/export_recent_issues_csv.py --days 14
python scripts/export_issues_for_jira.py --days 60
```

## Output Structure

All outputs are organized in timestamped folders under `gitlab_reports/`:

### Analysis Reports (`analysis_YYYYMMDD_HHMMSS/`)

- `analysis_report_YYYYMMDD_HHMMSS.txt` - Detailed text report
- `analysis_data_YYYYMMDD_HHMMSS.csv` - Structured CSV data
- Individual repository analysis files

### Markdown Issue Export (`issues_export_YYYYMMDD_HHMMSS/`)

- `ProjectName_issues_YYYYMMDD_HHMMSS.md` - Per-project issue files
- `issues_summary_YYYYMMDD_HHMMSS.md` - Summary with links

### CSV Issue Export (`issues_csv_YYYYMMDD_HHMMSS/`)

- `ProjectName_issues_YYYYMMDD_HHMMSS.csv` - Per-project CSV files
- `all_issues_consolidated_YYYYMMDD_HHMMSS.csv` - All issues combined
- `csv_export_summary_YYYYMMDD_HHMMSS.txt` - Export summary

### Jira Import (`jira_YYYYMMDD_HHMMSS/`)

- `ProjectName_jira_import_YYYYMMDD_HHMMSS.csv` - Per-project Jira files
- `all_issues_jira_import_YYYYMMDD_HHMMSS.csv` - Consolidated Jira import
- `jira_import_summary_YYYYMMDD_HHMMSS.txt` - Import instructions

## Configuration### Quick Setup1. **Copy configuration template:** `bash   cp config/env.template .env   `2. **Edit `.env` file with your settings:** `env   # GitLab instance URL   GITLAB_URL=https://gitlab.ptc-telematik.de      # Personal Access Token (required)   GITLAB_TOKEN=your_token_here   `3. **Verify configuration:** `bash   python config/settings.py   `### Advanced ConfigurationThe configuration system supports many optional settings. See `config/README.md` for complete documentation.**Key optional settings:**- `DEFAULT_ANALYSIS_DAYS` - Default analysis period- `DEFAULT_AUTHORS` - Default author filter- `EXCLUDE_REPOSITORIES` - Repositories to skip- `CODE_FILE_EXTENSIONS` - File types to analyze

### Command Line Options

| Option     | Description                    | Default |
| ---------- | ------------------------------ | ------- |
| `--days N` | Number of days back to analyze | 60      |
| `--help`   | Show help information          | -       |

## Advanced Usage

### Repository Analysis Features

- **Email Consolidation**: Automatically groups commits by author email
- **Activity Patterns**: Identifies peak development periods
- **Commit Frequency**: Tracks commits per day/week/month
- **File Change Analysis**: Most modified files and directories

### Issue Export Features

- **Recent Filter**: Only exports issues created/updated in specified timeframe
- **Full Context**: Includes descriptions, comments, assignees, labels
- **User Information**: Preserves author and assignee details
- **Cross-References**: Maintains links to original GitLab issues

### Jira Import Optimization

- **Field Mapping**: Automatically maps GitLab fields to Jira equivalents
- **User Context**: Includes full user information in descriptions
- **Priority Mapping**: Intelligent priority assignment based on labels
- **Component Detection**: Extracts components from labels and repository names

## Troubleshooting

### Common Issues

1. **"GitLab private token not found"**

   - Ensure `.env` file exists with `GITLAB_TOKEN` set
   - Verify token has `api` and `read_repository` scopes

2. **"Projects directory not found"**

   - Create `projects/` directory in project root
   - Clone your GitLab repositories into `projects/`

3. **"Could not access GitLab project"**

   - Verify repository URLs in `projects/` match GitLab projects
   - Check that your token has access to the repositories

4. **Permission errors**
   - Ensure you have write permissions in the project directory
   - Check that `gitlab_reports/` directory can be created

### Debug Mode

Add verbose output to any script:

```bash
python scripts/analyze_local_repos.py --days 30 --verbose
```

## Contributing

1. Fork the repository at [https://github.com/pouladzade/gitlab-analysis](https://github.com/pouladzade/gitlab-analysis)2. Create a feature branch (`git checkout -b feature/amazing-feature`)3. Commit your changes (`git commit -m 'Add amazing feature'`)4. Push to the branch (`git push origin feature/amazing-feature`)5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Version History

- **v1.0.0** - Initial release with organized project structure
  - Unified entry point
  - Organized folder structure
  - Comprehensive documentation
  - Timestamped output directories

## Support

For issues and questions:1. Check the troubleshooting section above2. Search existing GitHub issues at [https://github.com/pouladzade/gitlab-analysis/issues](https://github.com/pouladzade/gitlab-analysis/issues)3. Create a new issue with:

- Description of the problem
- Steps to reproduce
- Error messages
- Environment details (OS, Python version)

---

**Happy Analyzing! 🚀**
