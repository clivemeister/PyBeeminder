# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

PyBeeminder is a collection of Python utilities for interacting with the Beeminder API. The project consists of:

1. **Core API wrapper** (`beeminder.py`): A lightweight class that wraps Beeminder API v1 endpoints
2. **Standalone utilities**: Command-line scripts that use the API wrapper for specific tasks

This is a personal utility collection, not a library. Each script is designed to be run independently from the command line.

## Architecture

### Core Module: beeminder.py

The `Beeminder` class provides the foundational API interaction layer:

- **Initialization**: Can be instantiated either from an INI file (preferred for CLI tools) or by passing credentials directly
- **API methods**: Implements GET/POST/PUT patterns for user, goals, datapoints, and road updates
- **Authentication**: Uses auth_token from beeminder.ini (format in "beeminder sample.ini")
- **Base URL**: All API calls go through `https://www.beeminder.com/api/v1/`

Key methods:
- `get_user()`, `get_goals()`, `get_goal(goalname)`: Retrieve user/goal data
- `get_datapoints(goalname)`, `create_datapoint(...)`: Manage datapoints
- `update_road(goalname, new_roadall)`: Modify goal road (red line)

### Utility Scripts

All scripts follow a common pattern:
1. Use `argparse` for CLI arguments with `-h/--help` support
2. Initialize `Beeminder` from INI file (default: `beeminder.ini`, customizable via `--ini`)
3. Include `-v/--verbose` flags where appropriate
4. Include `-t/--test` flags for dry-run operations where they modify data

**listRedGoals.py**: Lists all goals with color-coded urgency (red/amber/blue/green) based on losedate

**addPointForRed.py**: Conditional datapoint creator
- Counts red goals across account
- Adds datapoint to a target goal based on red goal count
- Use case: Meta-tracking of goal urgency

**getTodoistOverdue.py**: Todoist integration
- Requires `todoist_api_python` package and todoist_token in INI
- Counts overdue Todoist tasks and posts count to specified Beeminder goal

**getRoad.py / setRoad.py**: Road manipulation utilities
- `getRoad.py`: Exports goal road matrix to CSV format
- `setRoad.py`: Imports CSV and updates goal road via API
- CSV format: `date, value, slope` where any field can be `None`
- Dates are converted to Unix timestamps (mid-day)

## Development Commands

### Running Scripts

All scripts are invoked directly with Python:

```bash
python listRedGoals.py
python addPointForRed.py -g goalname -t -v
python getTodoistOverdue.py -g goalname --ini beeminder.ini
python getRoad.py -g goalname -f output.csv
python setRoad.py -g goalname -f input.csv -v
```

### Setup Requirements

1. **Create credentials file** (first time only):
   ```bash
   cp "beeminder sample.ini" beeminder.ini
   ```
   Then edit `beeminder.ini` to add your credentials:
   - username: Your Beeminder username
   - auth_token: From https://www.beeminder.com/settings/account#account-permissions
   - todoist_token: (Optional) From https://todoist.com/app/settings/integrations/developer

2. **Install Python dependencies**:
   ```bash
   pip install requests
   pip install todoist_api_python  # Only needed for getTodoistOverdue.py
   ```

### Testing Scripts

Use the `-t` or `--test` flag on scripts that modify data to see what would happen without making changes:

```bash
python addPointForRed.py -g metawork -t -v
python getTodoistOverdue.py -g overdue -t
```

### Common Patterns

When adding new utilities:
- Import `Beeminder` class: `from beeminder import Beeminder`
- Initialize with INI: `pyminder = Beeminder(ini_file="beeminder.ini")`
- Use `argparse` with version number, help text, and common flags (`--ini`, `-v`, `-t`)
- Handle datetime conversions: Beeminder uses Unix timestamps, scripts often work with `datetime.datetime`
- For datapoint creation, use `time.mktime(now.timetuple())` to convert to timestamp

### API Error Handling

The `Beeminder._call()` method raises exceptions for non-200 status codes with format:
```
API request {method} {url} failed with code {status_code}: {response_text}
```

## Important Notes

- **No package management**: This project doesn't use setuptools/pip packaging. Scripts are run directly.
- **No tests**: Currently no test suite. Manual testing using `-t` flags where available.
- **Credentials**: Never commit `beeminder.ini` (already in .gitignore). Use the sample file as template.
- **Todoist integration**: Optional dependency - only needed for `getTodoistOverdue.py`
- **Road format**: The "roadall" structure is `[timestamp, value, rate]` where 2 of 3 must be specified per segment
