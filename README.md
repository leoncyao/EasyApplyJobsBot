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

### Local Installation

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

### Docker Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/EasyApplyJobsBot.git
cd EasyApplyJobsBot
```

2. Create your environment file:
```bash
cp .env.example .env
```

3. Edit `.env` with your credentials and settings:
```bash
nano .env
```

4. Create data directory:
```bash
mkdir -p data
```

5. Build and run with Docker Compose:
```bash
docker-compose up -d
```

The bot will run in the background and restart automatically unless stopped.

To view logs:
```bash
docker-compose logs -f
```

To stop the bot:
```bash
docker-compose down
```

## Data Persistence

- All data files are stored in the `data/` directory
- The directory is mounted as a volume in Docker
- Your data persists between container restarts

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `LINKEDIN_EMAIL`: Your LinkedIn email
- `LINKEDIN_PASSWORD`: Your LinkedIn password
- `HEADLESS`: Set to true for headless mode
- `BOT_SPEED`: Bot operation speed (default: 0.5)
- `MAX_APPLICATIONS`: Maximum applications per run
- `CHROME_PROFILE_PATH`: Path to Chrome profile (optional)
- `DEBUG_PORT`: Chrome debugging port
- `KEYWORDS`: Job search keywords
- `LOCATION`: Job search location
- `DISTANCE`: Search radius in miles
- `EXPERIENCE_LEVEL`: Experience level filter
- `JOB_TYPE`: Job type filter
- `WORKPLACE_TYPE`: Workplace type filter

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

