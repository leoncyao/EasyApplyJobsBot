# LinkedIn Easy Apply Bot (PyChrome Version)

A Python-based bot that automates the LinkedIn Easy Apply process using Chrome DevTools Protocol. This is a PyChrome version of the original [EasyApplyJobsBot](https://github.com/wodsuz/EasyApplyJobsBot).

## Features

- 🔍 Scrapes LinkedIn job listings
- 🤖 Automatically applies to jobs using Easy Apply
- 📝 Handles various form fields (text inputs, select dropdowns, radio buttons, checkboxes)
- 📊 Tracks application status and results
- 🔄 Supports retrying failed applications
- 📈 Configurable limits for job scraping and applications

## Prerequisites

- Python 3.x
- Chrome browser
- LinkedIn account

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/EasyApplyJobsBot.git
cd EasyApplyJobsBot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your settings in `config.py`:
- Add your LinkedIn credentials
- Adjust bot speed and other parameters
- Set your preferred job search criteria

## Starting Chrome in Debug Mode

Before running the bot, you need to start Chrome in debugging mode:

### Windows
1. Create a file named `start_chrome.ps1` with the following content:
```powershell
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$debugPort = 9222
$userDataDir = "$env:LOCALAPPDATA\Google\Chrome\Debug"

# Create debug directory if it doesn't exist
if (-not (Test-Path $userDataDir)) {
    New-Item -ItemType Directory -Path $userDataDir | Out-Null
}

# Start Chrome with debugging enabled
Start-Process $chromePath -ArgumentList "--remote-debugging-port=$debugPort", "--user-data-dir=`"$userDataDir`""
```

2. Run the script in PowerShell:
```powershell
.\start_chrome.ps1
```

### Linux
1. Create a file named `start_chrome.sh` with the following content:
```bash
#!/bin/bash

# Create debug profile directory if it doesn't exist
DEBUG_DIR="$HOME/.config/chrome-debug"
mkdir -p "$DEBUG_DIR"

# Start Chrome with debugging enabled
google-chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="$DEBUG_DIR" \
    --no-first-run \
    --no-default-browser-check
```

2. Make the script executable:
```bash
chmod +x start_chrome.sh
```

3. Run the script:
```bash
./start_chrome.sh
```

### Mac
1. Create a file named `start_chrome.sh` with the following content:
```bash
#!/bin/bash

# Create debug profile directory if it doesn't exist
DEBUG_DIR="$HOME/Library/Application Support/Chrome/Debug"
mkdir -p "$DEBUG_DIR"

# Start Chrome with debugging enabled
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="$DEBUG_DIR" \
    --no-first-run \
    --no-default-browser-check
```

2. Make the script executable:
```bash
chmod +x start_chrome.sh
```

3. Run the script:
```bash
./start_chrome.sh
```

## Usage

### Basic Usage

1. Start Chrome in debug mode using the instructions above
2. Run the bot with default settings:
```bash
python run_bot.py
```

### Advanced Options

```bash
python run_bot.py [options]

Options:
  --email EMAIL       LinkedIn email (defaults to config.py)
  --password PASSWORD LinkedIn password (defaults to config.py)
  --skip-scraping     Skip URL scraping and use existing job_urls.json
  --retry-failed      Retry failed applications
  --skip-login        Skip LinkedIn login (useful if already logged in)
  --verbose, -v       Enable verbose output
```

## Main Components

- `run_bot.py`: Main entry point for running the bot
- `pychrome_scraper.py`: Handles job listing scraping
- `pychrome_applier.py`: Manages the application process
- `pychrome_batch_applier.py`: Handles batch processing of multiple jobs
- `config.py`: Configuration settings
- `constants.py`: Bot constants and parameters
- `utils.py`: Utility functions
- `login.py`: LinkedIn login functionality

## Data Files

The bot maintains several JSON files in the `data/` directory:
- `job_data.json`: Stores job listings and their status
- `failed_applications.json`: Tracks failed applications
- `application_results.json`: Records application results
- `questions.json`: Stores encountered application questions

## Configuration

Key settings in `config.py`:
- LinkedIn credentials
- Job search parameters
- Bot behavior settings
- Logging preferences

## Troubleshooting

### Chrome Debug Mode Issues
- If Chrome fails to start in debug mode, ensure no other Chrome instances are running
- Check if port 9222 is available and not blocked by firewall
- Verify Chrome installation path in the start script
- Try running PowerShell as administrator if you encounter permission issues

## Limitations

- Limited to 50 successful applications per run
- Requires manual intervention for complex application forms
- May need adjustments for LinkedIn UI changes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original EasyApplyJobsBot by [wodsuz](https://github.com/wodsuz/EasyApplyJobsBot)
- [automated-bots.com](https://www.automated-bots.com/)


PyChrome Version 

