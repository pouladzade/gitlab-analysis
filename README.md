## GitLab Analysis Tool

A comprehensive Python tool for analyzing GitLab repositories and exporting issues in various formats. This tool provides detailed commit analysis, author statistics, and flexible issue export capabilities.**Repository:** [https://github.com/pouladzade/gitlab-analysis](https://github.com/pouladzade/gitlab-analysis)

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

## Configuration:

Quick Setup1. **Copy configuration template:** `bash   cp config/env.template .env   `2. **Edit `.env` file with your settings:** `env   # GitLab instance URL   GITLAB_URL=https://gitlab.ptc-telematik.de      # Personal Access Token (required)   GITLAB_TOKEN=your_token_here   `3. **Verify configuration:** `bash   python config/settings.py   `### Advanced ConfigurationThe configuration system supports many optional settings. See `config/README.md` for complete documentation.**Key optional settings:**- `DEFAULT_ANALYSIS_DAYS` - Default analysis period- `DEFAULT_AUTHORS` - Default author filter- `EXCLUDE_REPOSITORIES` - Repositories to skip- `CODE_FILE_EXTENSIONS` - File types to analyze

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
- **Offline Mode**: Enhanced support for analyzing local repositories
  - Automatically detects and tracks active repositories
  - Provides accurate repository inclusion summary
  - Supports local file URLs for repository references
  - Maintains consistent reporting between online and offline modes

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

# Enhanced Local Git Repository Analyzer

This tool analyzes your GitLab repositories for activity and author statistics, consolidating by email and supporting robust branch and date detection.

## Features

- Fetches all accessible GitLab repositories (not just those you are a member of)
- Detects activity on **all branches** (not just default)
- Supports SSH cloning (with custom port)
- Generates detailed reports (text and CSV) with:
  - Active/inactive repository summary
  - Author commit/line stats (when run in full mode)
- Supports `--list-only` mode for fast activity checks
- Handles merge commit exclusion, author consolidation, and more

## Setup

### 1. Environment Variables (.env)

Create a `.env` file in your project root with:

```
GITLAB_TOKEN=your_gitlab_token_here
GITLAB_URL=https://gitlab.ptc-telematik.de
```

- Your token must have `read_api` and `read_repository` scopes.

### 2. SSH Key Setup

- Add your public SSH key (e.g., `id_ed25519.pub`) to your GitLab account.
- Ensure your private key is loaded in your SSH agent:
  ```bash
  ssh-add ~/.ssh/id_ed25519
  ```
- Test with:
  ```bash
  ssh -T git@gitlab.ptc-telematik.de -p 7999
  ```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

## Usage

### List Only (no cloning, just activity summary)

```bash
python scripts/analyze_local_repo_enhanced.py --list-only --since 2024-04-25 --until 2024-05-25
```

### Full Online Analysis (fetch, clone/update, analyze)

```bash
python scripts/analyze_local_repo_enhanced.py --mode online --since 2024-04-25 --until 2024-05-25
```

### Offline Analysis (analyze already-cloned repos)

```bash
python scripts/analyze_local_repo_enhanced.py --mode offline --since 2024-04-25 --until 2024-05-25
```

### Verbose Output

Add `--verbose` to see detailed inclusion/skipping info for each repo.

## Report Interpretation

- **Active repositories (included):** Repos with at least one commit in the period (on any branch)
- **Non-active repositories (skipped):** No commits in the period
- **SUMMARY STATISTICS:** Author/commit/line stats (only in full analysis mode)

## Troubleshooting

- **No repositories found:**
  - Check your token and permissions
  - Increase `--max-repos` if you have many projects
- **No commits detected for a repo:**
  - Ensure the commit is pushed and visible via the API
  - Check the date range and timezone
  - Some GitLab API versions may have bugs with commit listing; try updating GitLab or using local analysis
- **No author stats:**
  - Make sure you run in full analysis mode (not `--list-only`)
  - Ensure repos are cloned and up to date

## Example .env

```
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_URL=https://gitlab.ptc-telematik.de
```

## Example SSH Test

```
ssh -T git@gitlab.ptc-telematik.de -p 7999
```

## Need Help?

- If you encounter issues with API access, check your token scopes and project visibility.
- For further debugging, use `--verbose` and review the printed API calls and results.
- If you need to analyze all branches for activity, the script already does this by default.

---

**For more advanced usage or troubleshooting, see the comments in the script or contact your GitLab admin.**
