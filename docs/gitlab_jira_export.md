# GitLab to Jira Issue Export Documentation

## Overview
This document describes the functionality and usage of the GitLab to Jira issue export scripts. These scripts facilitate the migration of issues from GitLab to Jira by exporting them in a Jira-compatible CSV format.

## Features

### Issue Mapping
The export process includes intelligent mapping of GitLab fields to Jira fields:

- **Issue Types**: Automatically mapped based on labels and title keywords
  - Bug: Contains keywords like 'bug', 'error', 'fix', 'defect'
  - Epic: Contains keyword 'epic'
  - Spike: Contains keywords like 'spike', 'research', 'investigation'
  - Story: Contains keywords like 'feature', 'story', 'user story'
  - Task: Default type if no other matches

- **Status Mapping**:
  - Closed → Done
  - Open with 'wip', 'in progress', 'doing' labels → In Progress
  - Open with 'review', 'testing', 'qa' labels → In Review
  - Other open issues → To Do

- **Priority Mapping**:
  - High: Contains keywords like 'high', 'urgent', 'critical', 'blocker'
  - Low: Contains keywords like 'low', 'minor'
  - Medium: Default priority

### Data Export
The export includes comprehensive issue data:

- Basic Information:
  - Issue Type
  - Summary (title)
  - Description
  - Status
  - Priority
  - Reporter
  - Assignee

- Additional Fields:
  - Labels
  - Components (extracted from labels and repository name)
  - Fix Version (from milestone)
  - Story Points (from weight)
  - Due Date
  - Created/Updated timestamps
  - External ID (GitLab issue ID)
  - Original URL
  - Repository name
  - GitLab Issue ID
  - Upvotes/Downvotes

### Export Formats
The system generates multiple output files:

1. **Individual Project CSVs**: Separate CSV files for each GitLab project
2. **Consolidated CSV**: Combined CSV file with all issues from all repositories
3. **Summary File**: Text file containing export statistics and instructions

## Usage

### Prerequisites
- Python 3.x
- GitLab API access token
- GitLab instance URL
- Local Git repositories cloned

### Environment Setup
Create a `.env` file with:
```
GITLAB_URL=https://your-gitlab-instance.com
GITLAB_TOKEN=your-private-token
```

### Running the Export
```bash
python scripts/export_issues_for_jira.py
```

### Export Options
- Default export period: 60 days
- Customizable export period via `days_back` parameter
- Automatic creation of timestamped export directories

## Output Structure

### Directory Structure
```
gitlab_reports/
└── jira_YYYYMMDD_HHMMSS/
    ├── project1_jira_import_YYYYMMDD_HHMMSS.csv
    ├── project2_jira_import_YYYYMMDD_HHMMSS.csv
    ├── all_issues_jira_import_YYYYMMDD_HHMMSS.csv
    └── jira_import_summary_YYYYMMDD_HHMMSS.txt
```

### CSV Format
The exported CSV files follow Jira's import format with the following columns:
1. Issue Type
2. Summary
3. Description
4. Status
5. Priority
6. Reporter
7. Assignee
8. Labels
9. Components
10. Fix Version
11. Story Points
12. Due Date
13. Created
14. Updated
15. External ID
16. Original URL
17. Repository
18. GitLab Issue ID
19. Upvotes
20. Downvotes

## Importing to Jira

1. In Jira, navigate to: System → External System Import → CSV
2. Upload the consolidated CSV file (`all_issues_jira_import_*.csv`)
3. Map the CSV columns to corresponding Jira fields
4. Review the import preview
5. Confirm the import

## Notes and Considerations

### Data Mapping
- The system uses intelligent mapping based on labels and content
- Custom mapping rules can be modified in the code
- Default mappings can be overridden by specific labels

### Limitations
- Jira import may have field limitations based on your instance
- Some GitLab-specific features may not have direct Jira equivalents
- Large exports may require Jira import in batches

### Best Practices
1. Review the exported data before importing to Jira
2. Test with a small subset of issues first
3. Back up Jira data before large imports
4. Verify field mappings in Jira before final import

## Troubleshooting

### Common Issues
1. **Authentication Errors**
   - Verify GitLab token permissions
   - Check GitLab URL configuration

2. **Missing Issues**
   - Verify repository access permissions
   - Check export date range

3. **Import Failures**
   - Verify CSV format compatibility
   - Check Jira field mappings
   - Review Jira import logs

### Support
For issues or questions:
1. Check the export logs in the summary file
2. Review the export statistics
3. Verify GitLab API access
4. Check Jira import requirements 