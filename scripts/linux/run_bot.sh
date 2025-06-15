#!/bin/bash

# Run the LinkedIn job bot with skip login, skip scraping, and retry failed options
# uv run main.py --verbose --retry-failed 
# uv run main.py --verbose --retry-failed  --skip-login
# uv run main.py --verbose --retry-failed  --skip-login --skip-scraping
# uv run main.py --verbose --retry-failed  --skip-login --skip-scraping --skip-applying
uv run main.py --verbose --retry-failed  --skip-login --skip-applying