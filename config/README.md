# Configuration Directory

This directory contains configuration files and templates for the GitLab Analysis Tool.

## Files

### `env.template`

Template file for environment variables. Copy this file to `.env` in the project root and customize the values.

### `settings.py`

Python module that manages configuration loading and validation.

## Setup Instructions

### 1. Create Environment File

Copy the template to create your environment configuration:

```bash
# From the project root directory
cp config/env.template .env
```

### 2. Configure GitLab Access

Edit the `.env` file and set your GitLab credentials:

```bash
# Required: Your GitLab instance URL
GITLAB_URL=https://your-gitlab-instance.com

# Required: Your personal access token
GITLAB_TOKEN=your_token_here
```

### 3. Generate GitLab Personal Access Token

1. Log into your GitLab instance
2. Go to **Profile → Access Tokens → Personal Access Tokens**
3. Create a new token with these scopes:
   - `api` - For GitLab API access
   - `read_repository` - For repository analysis
4. Copy the token to your `.env` file

### 4. Optional Configuration

You can customize additional settings in your `.env` file:

```bash
# Analysis settings
DEFAULT_ANALYSIS_DAYS=60
DEFAULT_AUTHORS=john.doe@company.com,jane.smith@company.com

# Directory settings
REPORTS_DIRECTORY=gitlab_reports
PROJECTS_DIRECTORY=projects

# Repository filtering
EXCLUDE_REPOSITORIES=archived-repo,test-repo

# File type filtering
CODE_FILE_EXTENSIONS=.py,.js,.java,.cpp,.c,.h,.cs,.php,.rb,.go,.ts

# Analysis mode
ANALYSIS_MODE=offline  # Set to 'offline' for local repository analysis only
```

## Usage

### Check Configuration

You can verify your configuration by running:

```bash
python config/settings.py
```

This will display a summary of your current configuration and validate that required settings are present.

### Use in Scripts

Import and use the configuration in your scripts:

```python
from config.settings import load_config

config = load_config()
print(f"GitLab URL: {config.gitlab_url}")
print(f"Default analysis days: {config.default_analysis_days}")
```

## Configuration Options

| Variable                | Description                    | Default                           | Required |
| ----------------------- | ------------------------------ | --------------------------------- | -------- |
| `GITLAB_URL`            | GitLab instance URL            | `https://gitlab.ptc-telematik.de` | ✓        |
| `GITLAB_TOKEN`          | Personal access token          | -                                 | ✓        |
| `DEFAULT_ANALYSIS_DAYS` | Default days for analysis      | `60`                              | ✗        |
| `REPORTS_DIRECTORY`     | Output directory for reports   | `gitlab_reports`                  | ✗        |
| `PROJECTS_DIRECTORY`    | Directory with cloned repos    | `projects`                        | ✗        |
| `CODE_FILE_EXTENSIONS`  | File types to analyze          | See template                      | ✗        |
| `DEFAULT_AUTHORS`       | Default author filter          | -                                 | ✗        |
| `EXCLUDE_REPOSITORIES`  | Repos to skip                  | -                                 | ✗        |
| `ANALYSIS_MODE`         | Analysis mode (online/offline) | `online`                          | ✗        |

## Security Notes

- **Never commit your `.env` file** - it contains sensitive tokens
- The `.env` file is already in `.gitignore`
- Rotate your GitLab tokens regularly
- Use tokens with minimal required permissions

## Troubleshooting

### "GitLab private token not found"

- Ensure `.env` file exists in project root
- Check that `GITLAB_TOKEN` is set in `.env`
- Verify token is valid and has required scopes

### "Could not access GitLab project"

- Check that your token has access to the repositories
- Verify the `GITLAB_URL` is correct
- Ensure repositories are cloned in the `projects/` directory

### Configuration validation

```bash
python config/settings.py
```

Will show current configuration and any validation errors.
