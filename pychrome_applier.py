import time, random, os, json
import utils, constants, config
import pychrome

from utils import _print

console_logs = []

class PyChromeJobApplier:
    def __init__(self, browser, tab, verbose=False):
        self.browser = browser
        self.tab = tab
        self.verbose = verbose
        _print(f"verbose: {verbose}", level="debug", verbose=verbose)

    def _set_language_to_english(self):
        """Set LinkedIn language to English"""
        self.tab.Page.navigate(url="https://www.linkedin.com/mypreferences/d/settings/language")
        time.sleep(1)
        
        script = """
        Array.from(document.querySelectorAll('select')).map(select => {
            select.selectedIndex = 6;
            select.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        });
        """
        _print("🔍 Changing language to English", level="info", verbose=self.verbose)
        time.sleep(2)
        result = self.tab.Runtime.evaluate(expression=script, returnByValue=True)
        time.sleep(2)
        return result

    def apply_to_job(self, job_url):
        """Main method to apply to a specific job"""
        time.sleep(1)
        _print(f"🔍 Applying to job: {job_url}", level="info", verbose=self.verbose)
        
        try:
            # self._set_language_to_english()
            # self._check_for_bengali_home()
            
            # Navigate to the job page
            self.tab.Page.navigate(url=job_url)
            time.sleep(1)  # Wait for page load

            # Check for Easy Apply button
            easy_apply_button = self._find_easy_apply_button()
            if not easy_apply_button:
                _print(f"🥳 Already applied! Job: {job_url}", level="info", verbose=self.verbose)
                return True

            time.sleep(1)

            if self._complete_application_process():
                _print(f"✅ Successfully applied to: {job_url}", level="success", verbose=self.verbose)
                return True
            else:
                _print(f"❌ Failed to apply to: {job_url}", level="error", verbose=self.verbose)
                return False

        except Exception as e:
            _print(f"Error during application process: {str(e)}", level="error", verbose=self.verbose)
            return False

    def _find_easy_apply_button(self):
        """Find the Easy Apply button using XPath"""
        script = """
        (function() {
            const button = document.querySelector('div.jobs-apply-button--top-card button.jobs-apply-button');
            if (button && button.textContent.toLowerCase().includes('easy')) {
                button.click();
                return true;
            }
            return false;
        })()
        """
        result = self.tab.Runtime.evaluate(expression=script, returnByValue=True)
        return result.get('result', {}).get('value', False)

    def _check_for_bengali_home(self):
        """Check if the page contains Bengali 'হোম' text in navigation elements"""
        time.sleep(1)
        script = """
        (function() {
            const targetText = "হোম";
            console.log("Looking for text:", targetText);
            
            const elements = document.querySelectorAll('span.t-12.global-nav__primary-link-text');
            console.log("Found elements:", elements.length);
            
            const bengaliElements = [];
            
            elements.forEach((element, index) => {
                const title = element.getAttribute('title') || '';
                const text = element.textContent.trim();
                
                console.log(`Element ${index}:`, {
                    title: title,
                    text: text,
                    innerHTML: element.innerHTML
                });
                
                if (title === targetText || text === targetText) {
                    console.log("Match found!");
                    bengaliElements.push({
                        title: title,
                        text: text,
                        innerHTML: element.innerHTML
                    });
                }
            });
            
            console.log("Total matches:", bengaliElements.length);
            
            if (bengaliElements.length > 0) {
                return {
                    found: true,
                    elements: bengaliElements
                };
            }
            return {
                found: false,
                elements: []
            };
        })()
        """
        result = self.tab.Runtime.evaluate(expression=script, returnByValue=True)

        time.sleep(1)
        result_value = result.get('result', {}).get('value', {})
        
        if result_value.get('found', False):
            elements = result_value.get('elements', [])
            for element in elements:
                _print(f"🚨 Found 'হোম' in element:", level="warning", verbose=self.verbose)
                _print(f"  Text Content: '{element['text']}'", level="debug", verbose=self.verbose)
                _print(f"  Title: '{element['title']}'", level="debug", verbose=self.verbose)
                _print(f"  Inner HTML: '{element['innerHTML']}'", level="debug", verbose=self.verbose)
            self._set_language_to_english()

            return False
        else:
            _print("✅ No 'হোম' text found in navigation elements.", level="success", verbose=self.verbose)
            return True

    def _complete_application_process(self):
        """Complete the multi-step application process"""
        max_attempts = 10
        attempt = 0

        while attempt < max_attempts:
            try:
                # if not self._check_for_bengali_home():
                #     return False
                
                time.sleep(1)
                self._handle_application_form()
                time.sleep(random.uniform(0.1, constants.botSpeed))
                
                if not self._find_continue_button():
                    _print("❌ No continue button", level="error", verbose=self.verbose)
                    if not self._find_review_button():
                        _print("❌ No review button", level="error", verbose=self.verbose)
                        if not self._find_submit_button():
                            _print("❌ No submit button", level="error", verbose=self.verbose)
                        else:
                            return True
                attempt += 1
            except Exception as e:
                _print(f"Error in application step: {str(e)}", level="error", verbose=self.verbose)
                return False

    def _handle_application_form(self):
        """Handle the job application form"""
        time.sleep(random.uniform(0.1, constants.botSpeed * 2))
        
        # Handle other text inputs
        self._handle_text_inputs_with_question_logging()
        time.sleep(1)
        self._handle_toronto_location()
        time.sleep(1)
        # Handle radio buttons and checkboxes
        self.handle_fieldset()
        time.sleep(1)
        # Handle select fields
        self._handle_select_fields()
        time.sleep(1)
        # Handle textareas
        self._handle_textareas()

    def handle_fieldset(self):
        """Handle radio inputs within fieldsets by selecting the first option"""
        
    
        script = """
        (function() {
            function handleFieldset(fieldset) {
                const inputs = Array.from(fieldset.querySelectorAll('input[type="radio"], input[type="checkbox"]'));
                if (!inputs.length) {
                    console.log('No radio/checkbox inputs found in this fieldset');
                    return null;
                }

                console.log(`Found ${inputs.length} radio/checkbox inputs in fieldset:`);
                
                // Log details of all inputs
                inputs.forEach((input, index) => {
                    const label = input.parentElement ? input.parentElement.textContent.trim() : 'No label';
                    console.log(`  Option ${index + 1}:`);
                    console.log(`    Label: ${label}`);
                    console.log(`    Type: ${input.type}`);
                });

                // Get the first input
                const firstInput = inputs[0];
                const firstLabel = firstInput.parentElement ? firstInput.parentElement.textContent.trim() : 'No label';
                
                console.log('\\nSelecting first option:');
                console.log(`  Label: ${firstLabel}`);
                console.log(`  Type: ${firstInput.type}`);

                try {
                    firstInput.checked = true;
                    firstInput.dispatchEvent(new Event('change', { bubbles: true }));
                    return {
                        label: firstLabel,
                        type: firstInput.type,
                        success: true
                    };
                } catch (error) {
                    console.error('Error selecting first option:', error);
                    return {
                        label: firstLabel,
                        type: firstInput.type,
                        success: false,
                        error: error.message
                    };
                }
            }

            const dialog = document.querySelector("[data-test-modal-id='easy-apply-modal']");
            if (!dialog) {
                console.log('No dialog found');
                return { success: false, error: 'No dialog found' };
            }

            const fieldsets = Array.from(dialog.querySelectorAll('fieldset'));
            console.log(`Found ${fieldsets.length} fieldsets`);

            const results = fieldsets.map((fieldset, index) => {
                console.log(`\\nProcessing fieldset ${index + 1}:`);
                const result = handleFieldset(fieldset);
                return {
                    fieldsetIndex: index + 1,
                    ...result
                };
            });

            return {
                success: true,
                results
            };
        })()
        """
        
        result = self.tab.Runtime.evaluate(expression=script, returnByValue=True)
        result_value = result.get('result', {}).get('value', {})
        
        if not result_value.get('success', False):
            _print(f"❌ Error handling fieldsets: {result_value.get('error', 'Unknown error')}", level="error", verbose=self.verbose)
            return False
            
        results = result_value.get('results', [])
        
        _print(f"✅ Processed {len(results)} fieldsets", level="success", verbose=self.verbose)
        
        return True

    def _handle_text_inputs_with_question_logging(self):
        """Handle text input fields with question logging"""
        # Read responses from JSON file
        try:
            with open('data/answers.json', 'r', encoding='utf-8') as f:
                input_responses = json.load(f)
        except FileNotFoundError:
            _print("❌ data/answers.json not found", level="error", verbose=self.verbose)
            return False
        except json.JSONDecodeError:
            _print("❌ Invalid data/answers.json", level="error", verbose=self.verbose)
            return False

        script = """
        (function() {
            const input_responses = %s;

            function sleep(ms) {
                const start = Date.now();
                while (Date.now() - start < ms) {
                    // Busy wait
                }
            }

            function simulateKeyboardEvents(input, value) {
                // Focus the input
                input.focus();
                
                // Clear existing value
                input.value = '';
                
                // Use execCommand to insert text
                document.execCommand('insertText', false, value);

                console.log('Continuing after delay...');
                // Simulate keyboard events regardless of value
                console.log(value.toLowerCase())
                console.log(value.toLowerCase() === 'toronto')
                if (value.toLowerCase() === 'toronto') {
                    console.log("MATCHED TORONTO")
                    sleep(10000)
                    // Simulate down arrow key press
                    input.dispatchEvent(new KeyboardEvent('keydown', {
                        key: 'ArrowDown',
                        code: 'ArrowDown',
                        keyCode: 40,
                        which: 40,
                        bubbles: true
                    }));
                    
                    // Simulate enter key press
                    input.dispatchEvent(new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        which: 13,
                        bubbles: true
                    }));
                }
                
                // Dispatch change event
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }

            function decideInputValue(input) {
                const parent = input.parentElement;
                const parentText = parent ? parent.textContent.toLowerCase() : '';
                const inputId = input.id.toLowerCase();
                const inputName = input.name ? input.name.toLowerCase() : '';
                const inputPlaceholder = input.placeholder ? input.placeholder.toLowerCase() : '';

                // Log input details for debugging
                console.log('\\nAnalyzing input:');
                console.log(`  ID: ${inputId}`);
                console.log(`  Name: ${inputName}`);
                console.log(`  Placeholder: ${inputPlaceholder}`);
                console.log(`  Parent text: ${parentText}`);

                // Check each response pattern
                for (const [keywords, value] of Object.entries(input_responses)) {
                    const keywordList = keywords.split(',');
                    
                    // Check if any of the keywords match any of the input's properties
                    const matches = keywordList.some(keyword => 
                        parentText.includes(keyword) || 
                        inputId.includes(keyword) ||
                        inputName.includes(keyword) ||
                        inputPlaceholder.includes(keyword)
                    );

                    if (matches) {
                        console.log(`  Matched with keywords: ${keywords}`);
                        console.log(`  Setting value to: ${value}`);
                        return value;
                    }
                }

                // No match found, use default
                console.log('  No match found, using default value: 5');
                return '5';
            }

            function fillInput(input) {
                if (!input) return false;
                
                try {
                    const value = decideInputValue(input);
                    simulateKeyboardEvents(input, value);
                    return true;
                } catch (error) {
                    console.error('Error filling input:', error);
                    return false;
                }
            }

            const dialog = document.querySelector("[data-test-modal-id='easy-apply-modal']");
            if (!dialog) {
                console.log('No dialog found');
                return { success: false, error: 'No dialog found' };
            }

            const inputs = Array.from(dialog.querySelectorAll('input[type="text"]'));
            console.log(`Found ${inputs.length} text input fields`);

            const results = inputs.map(input => {
                sleep(1000);
                const success = fillInput(input);
                
                // Get parent text using XPath
                let parentText = '';
                try {
                    const parentXPath = `//input[@id='${input.id}']/..`;
                    const parentElement = document.evaluate(
                        parentXPath,
                        document,
                        null,
                        XPathResult.FIRST_ORDERED_NODE_TYPE,
                        null
                    ).singleNodeValue;
                    
                    if (parentElement) {
                        parentText = parentElement.textContent.trim();
                    }
                } catch (e) {
                    console.error('Error getting parent text:', e);
                }

                return {
                    id: input.id,
                    name: input.name,
                    placeholder: input.placeholder,
                    value: input.value,
                    success,
                    question: input.parentElement ? input.parentElement.textContent.trim() : '',
                    parentText: parentText
                };
            });

            return {
                success: true,
                results
            };
        })()
        """ % json.dumps(input_responses)
        
        result = self.tab.Runtime.evaluate(expression=script, returnByValue=True)
        result_value = result.get('result', {}).get('value', {})
        
        if not result_value.get('success', False):
            _print(f"❌ Error handling text inputs: {result_value.get('error', 'Unknown error')}", level="error", verbose=self.verbose)
            return False
            
        results = result_value.get('results', [])
        _print(f"✅ Processed {len(results)} text input fields", level="success", verbose=self.verbose)
        
        # Log new questions
        try:
            # Read existing questions
            if os.path.exists('data/questions.json'):
                with open('data/questions.json', 'r', encoding='utf-8') as f:
                    existing_texts = json.load(f)
            else:
                existing_texts = []
            
            # Get new parent texts from results
            new_texts = []
            for result in results:
                if result.get('parentText') and result['parentText'] not in existing_texts:
                    new_texts.append(result['parentText'])
            
            # Add new texts to existing ones
            if new_texts:
                existing_texts.extend(new_texts)
                # Save updated texts
                with open('data/questions.json', 'w', encoding='utf-8') as f:
                    json.dump(existing_texts, f, indent=2, ensure_ascii=False)
                _print(f"📝 Added {len(new_texts)} new parent texts to questions.json", level="info", verbose=self.verbose)
        
        except Exception as e:
            _print(f"❌ Error logging parent texts: {str(e)}", level="error", verbose=self.verbose)
        
        return True


    def _handle_select_fields(self):
        """Handle select/dropdown fields"""
        script = """
        (function() {
            const dialog = document.querySelector("[data-test-modal-id='easy-apply-modal']");
            if (!dialog) {
                return { success: false, message: "No dialog found" };
            }
            
            const selects = dialog.querySelectorAll('select');
            const results = [];
            
            selects.forEach(select => {
                const label = select.previousElementSibling?.textContent?.trim() || 'No label';
                results.push({ label });
                
                if (select.options.length > 1) {
                    select.selectedIndex = 1;
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
            
            return { 
                success: true, 
                fields: results 
            };
        })()
        """
        try:
            result = self.tab.Runtime.evaluate(expression=script, returnByValue=True)
            result_value = result.get('result', {}).get('value', {})
            
            if result_value.get('success', False):
                fields = result_value.get('fields', [])
                _print(f"Found {len(fields)} select fields:", level="info", verbose=self.verbose)
                for field in fields:
                    _print(f"  • {field['label']}", level="info", verbose=self.verbose)
                return True
            else:
                _print("ℹ️ No select fields found in this application", level="info", verbose=self.verbose)
                return False
                
        except Exception as e:
            _print(f"❌ Error handling select fields: {str(e)}", level="error", verbose=self.verbose)
            return False

    def _handle_textareas(self):
        """Handle textarea fields"""
        script = """
        (function() {
            const textarea_responses = {
                'cover,letter': 'I am excited to apply for this position. I believe my skills and experience make me a strong candidate for this role.',
                'message': 'Thank you for considering my application. I look forward to discussing how I can contribute to your team.',
                'additional,information': 'I am available for an interview at your convenience and can start immediately.',
                'why,interested': 'I am particularly interested in this role because it aligns with my career goals and offers opportunities for growth.',
                'experience': 'I have extensive experience in software development and am passionate about creating efficient solutions.',
                'skills': 'My key skills include software development, problem-solving, and team collaboration.'
            };

            function decideTextareaValue(textarea) {
                const parent = textarea.parentElement;
                const parentText = parent ? parent.textContent.toLowerCase() : '';
                const textareaId = textarea.id.toLowerCase();
                const textareaName = textarea.name ? textarea.name.toLowerCase() : '';
                const textareaPlaceholder = textarea.placeholder ? textarea.placeholder.toLowerCase() : '';

                // Check each response pattern
                for (const [keywords, value] of Object.entries(textarea_responses)) {
                    const keywordList = keywords.split(',');
                    
                    // Check if any of the keywords match any of the textarea's properties
                    const matches = keywordList.some(keyword => 
                        parentText.includes(keyword) || 
                        textareaId.includes(keyword) ||
                        textareaName.includes(keyword) ||
                        textareaPlaceholder.includes(keyword)
                    );

                    if (matches) {
                        console.log(`  Matched with keywords: ${keywords}`);
                        console.log(`  Setting value to: ${value}`);
                        return value;
                    }
                }

                // Default response if no match found
                console.log('  No match found, using default response');
                return 'I am a software engineer with a passion for building scalable and efficient systems.';
            }

            function fillTextarea(textarea) {
                if (!textarea) return false;
                
                try {
                    const value = decideTextareaValue(textarea);
                    textarea.value = value;
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                    textarea.dispatchEvent(new Event('change', { bubbles: true }));
                    return true;
                } catch (error) {
                    console.error('Error filling textarea:', error);
                    return false;
                }
            }

            const dialog = document.querySelector("[data-test-modal-id='easy-apply-modal']");
            if (!dialog) {
                console.log('No dialog found');
                return { success: false, error: 'No dialog found' };
            }

            const textareas = Array.from(dialog.querySelectorAll('textarea'));
            console.log(`Found ${textareas.length} textarea fields`);

            const results = textareas.map(textarea => {
                const success = fillTextarea(textarea);
                return {
                    id: textarea.id,
                    name: textarea.name,
                    placeholder: textarea.placeholder,
                    value: textarea.value,
                    success
                };
            });

            return {
                success: true,
                results
            };
        })()
        """
        
        result = self.tab.Runtime.evaluate(expression=script, returnByValue=True)
        result_value = result.get('result', {}).get('value', {})
        
        if not result_value.get('success', False):
            _print(f"❌ Error handling textareas: {result_value.get('error', 'Unknown error')}", level="error", verbose=self.verbose)
            return False
            
        results = result_value.get('results', [])
        _print(f"✅ Processed {len(results)} textarea fields", level="success", verbose=self.verbose)
        
        return True

    def _find_continue_button(self):
        """Find and click the Continue button"""
        script = """
        (function() {
            const button = document.querySelector('button[aria-label="Continue to next step"]');
            if (button) {
                button.click();
                return true;
            }
            return false;
        })()
        """
        result = self.tab.Runtime.evaluate(expression=script, returnByValue=True)
        return result.get('result', {}).get('value', False)

    def _find_review_button(self):
        """Find and click the Review button"""
        script = """
        (function() {
            const button = document.querySelector('button[aria-label="Review your application"]');
            if (button) {
                button.click();
                return true;
            }
            return false;
        })()
        """
        result = self.tab.Runtime.evaluate(expression=script, returnByValue=True)
        return result.get('result', {}).get('value', False)

    def _find_submit_button(self):
        """Find and click the Submit button"""
        script = """
        (function() {
            const button = document.querySelector('button[aria-label="Submit application"]');
            if (button) {
                button.click();
                return true;
            }
            return false;
        })()
        """
        result = self.tab.Runtime.evaluate(expression=script, returnByValue=True)
        return result.get('result', {}).get('value', False)

    def _log_question(self, question_text):
        """Log new questions to a JSON file"""
        try:
            if not os.path.exists('data'):
                os.makedirs('data')
            
            if os.path.exists('data/job_questions.json'):
                with open('data/job_questions.json', 'r', encoding='utf-8') as f:
                    questions = json.load(f)
            else:
                questions = []
            
            if question_text and question_text not in questions:
                questions.append(question_text)
                with open('data/job_questions.json', 'w', encoding='utf-8') as f:
                    json.dump(questions, f, indent=2, ensure_ascii=False)
                prYellow(f"📝 Logged new question: {question_text}")
        except Exception as e:
            _print(f"❌ Error logging question: {str(e)}", level="error", verbose=self.verbose)

    def _handle_toronto_location(self):
        """Handle the Toronto location input specifically"""
        # First command: Find input and insert text
        insert_script = """
        (function() {
            const dialog = document.querySelector("[data-test-modal-id='easy-apply-modal']");
            if (!dialog) {
                console.log('No dialog found');
                return { success: false, error: 'No dialog found' };
            }

            const locationInput = dialog.querySelector('input[id*="location"], input[id*="city"]');
            if (!locationInput) {
                console.log('No location input found');
                return { success: false, error: 'No location input found' };
            }

            console.log('Found location input, inserting Toronto...');
            
            // Focus and clear
            locationInput.focus();
            locationInput.value = '';
            
            // Type Toronto
            document.execCommand('insertText', false, 'Toronto');
            console.log('Typed Toronto');
            
            return {
                success: true,
                value: locationInput.value
            };
        })()
        """
        
        result = self.tab.Runtime.evaluate(expression=insert_script, returnByValue=True)
        result_value = result.get('result', {}).get('value', {})
        
        if not result_value.get('success', False):
            _print("ℹ️ No city or location field found in this application", level="info", verbose=self.verbose)
            return False
            
        # Wait for suggestions
        time.sleep(2)
        
        # Second command: Press down arrow
        down_script = """
        (function() {
            const dialog = document.querySelector("[data-test-modal-id='easy-apply-modal']");
            const locationInput = dialog.querySelector('input[id*="location"], input[id*="city"]');
            
            console.log('Pressing down arrow...');
            locationInput.dispatchEvent(new KeyboardEvent('keydown', {
                key: 'ArrowDown',
                code: 'ArrowDown',
                keyCode: 40,
                which: 40,
                bubbles: true
            }));
            
            return { success: true };
        })()
        """
        
        result = self.tab.Runtime.evaluate(expression=down_script, returnByValue=True)
        if not result.get('result', {}).get('value', {}).get('success', False):
            _print("❌ Error pressing down arrow", level="error", verbose=self.verbose)
            return False
            
        # Wait a bit
        time.sleep(1)
        
        # Third command: Press enter
        enter_script = """
        (function() {
            const dialog = document.querySelector("[data-test-modal-id='easy-apply-modal']");
            const locationInput = dialog.querySelector('input[id*="location"], input[id*="city"]');
            
            console.log('Pressing enter...');
            locationInput.dispatchEvent(new KeyboardEvent('keydown', {
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                which: 13,
                bubbles: true
            }));
            
            // Dispatch change event
            locationInput.dispatchEvent(new Event('change', { bubbles: true }));
            
            return {
                success: true,
                value: locationInput.value
            };
        })()
        """
        
        result = self.tab.Runtime.evaluate(expression=enter_script, returnByValue=True)
        result_value = result.get('result', {}).get('value', {})
        
        if not result_value.get('success', False):
            _print("❌ Error pressing enter", level="error", verbose=self.verbose)
            return False
            
        _print(f"✅ Set location to: {result_value.get('value', '')}", level="success", verbose=self.verbose)
        return True

if __name__ == "__main__":
    import argparse
    from login import connect_to_chrome, login_to_linkedin
    import config
    
    parser = argparse.ArgumentParser(description='Apply to a specific LinkedIn job using PyChrome')
    parser.add_argument('--url', required=True, help='LinkedIn job URL to apply to')
    parser.add_argument('--email', default=config.email, help='LinkedIn email (defaults to config.py)')
    parser.add_argument('--password', default=config.password, help='LinkedIn password (defaults to config.py)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Get credentials from config.py if not provided via command line
    email = args.email or config.email
    password = args.password or config.password
    
    if not email or not password:
        print("Error: LinkedIn credentials not found. Please provide them via command line arguments or in config.py")
        exit(1)
    
    try:
        # First connect to Chrome and login
        browser, tab = connect_to_chrome(verbose=args.verbose)
        if not browser or not tab:
            print("Error: Failed to connect to Chrome")
            exit(1)
            
        if not login_to_linkedin(tab, email, password, args.verbose):
            print("Error: Failed to login to LinkedIn")
            exit(1)
            
        # Initialize applier with browser and tab
        applier = PyChromeJobApplier(browser=browser, tab=tab)
        applier.apply_to_job(args.url)
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)