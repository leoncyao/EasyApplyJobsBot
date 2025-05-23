import time, random, os, json
import pychrome
from .utils import _print
from .constants import *
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def connect_to_chrome(debugging_url="http://127.0.0.1:9222", verbose=False):
    """Connect to Chrome and set up the tab"""
    try:
        browser = pychrome.Browser(url=debugging_url)
        tabs = browser.list_tab()
        if not tabs:
            raise Exception("No tabs found in the browser")
        
        tab = tabs[0]
        tab.start()
        
        # Enable necessary domains
        tab.Network.enable()
        tab.Page.enable()
        tab.Runtime.enable()
        tab.DOM.enable()
        tab.Console.enable()

        _print("Successfully connected to Chrome", "success", verbose)
        return browser, tab
    except Exception as e:
        _print(f"Failed to connect to Chrome: {str(e)}", "error", verbose)
        return None, None

def login_to_linkedin(tab, email, password, verbose=False):
    """Login to LinkedIn using Chrome DevTools Protocol"""
    if not email or not password:
        raise ValueError("Email and password must be provided")

    _print("Trying to log in to LinkedIn...", "info", verbose)
    try:
        # Navigate to LinkedIn login page
        tab.Page.navigate(url="https://www.linkedin.com/checkpoint/rm/sign-in-another-account")
        time.sleep(random.uniform(2, 3))  # Wait for page to load

        # Fill in username
        username_script = f"""
        document.querySelector('#username').value = '{email}';
        """
        tab.Runtime.evaluate(expression=username_script)
        time.sleep(random.uniform(0.5, 1))

        # Fill in password
        password_script = f"""
        document.querySelector('#password').value = '{password}';
        """
        tab.Runtime.evaluate(expression=password_script)
        time.sleep(random.uniform(0.5, 1))

        # Click submit button
        submit_script = """
        document.querySelector('button[type="submit"]').click();
        """
        tab.Runtime.evaluate(expression=submit_script)

        # Wait for login to complete
        time.sleep(10)

        # # Check if login was successful by looking for common elements that appear after login
        # check_login_script = """
        # document.querySelector('.global-nav') !== null;
        # """
        # result = tab.Runtime.evaluate(expression=check_login_script)
        
        # if result.get('result', {}).get('value', False):
        #     _print("Successfully logged in to LinkedIn", "success", verbose)
        #     return True
        # else:
        #     _print("Login failed - could not verify successful login", "error", verbose)
        #     return False

    except Exception as e:
        _print(f"Error during login: {str(e)}", "error", verbose)
        raise

if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    import os
    
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Login to LinkedIn using Chrome DevTools')
    parser.add_argument('--debug-url', default="http://localhost:9222", 
                      help='Chrome DevTools debugging URL (default: http://localhost:9222)')
    parser.add_argument('--email',
                      help='LinkedIn email address (defaults to .env)')
    parser.add_argument('--password',
                      help='LinkedIn password (defaults to .env)')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Get credentials from .env if not provided via command line
    email = args.email or os.getenv('EMAIL')
    password = args.password or os.getenv('PASSWORD')
    
    if not email or not password:
        print("Error: LinkedIn credentials not found. Please provide them via command line arguments or in .env file")
        exit(1)
    
    try:
        browser, tab = connect_to_chrome(args.debug_url, args.verbose)
        if browser and tab:
            login_to_linkedin(tab, email, password, args.verbose)
    except Exception as e:
        print(f"Error: {e}")
