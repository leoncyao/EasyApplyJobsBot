import time, random, os, json
import utils, constants, config
import pychrome
from utils import prRed, prYellow, prGreen


console_logs = []

class PyChromeJobApplier:
    def __init__(self, debugging_url="http://127.0.0.1:9222"):
        """Initialize the applier with Chrome DevTools debugging URL"""
        self.debugging_url = debugging_url
        self.browser = None
        self.tab = None

    def connect(self):
        """Connect to Chrome and set up the tab"""
        try:
            self.browser = pychrome.Browser(url=self.debugging_url)
            tabs = self.browser.list_tab()
            if not tabs:
                raise Exception("No tabs found in the browser")
            
            self.tab = tabs[0]


            self.tab.start()
            self.tab.Log.enable()
            # Enable necessary domains
            self.tab.Network.enable()
            self.tab.Page.enable()
            self.tab.Runtime.enable()
            self.tab.DOM.enable()
            self.tab.Console.enable()  # Enable Console domain
            

            # def handle_console(event):
            #     for arg in event.get("args", []):
            #         value = arg.get("value")
            #         if value:
            #             global console_logs
            #             console_logs.append(value)

            # # Add event listener for console output
            # self.tab.Runtime.consoleAPICalled = handle_console


            prGreen("✅ Successfully connected to Chrome")
            return True
        except Exception as e:
            prRed(f"❌ Failed to connect to Chrome: {str(e)}")
            return False

    def apply_to_job(self, job_url):
        """Main method to apply to a specific job"""
        if not self.connect():
            return False

        try:
            # Navigate to the job page
            self.tab.Page.navigate(url=job_url)
            time.sleep(3)  # Wait for page load

            # Check for Easy Apply button
            easy_apply_button = self._find_easy_apply_button()
            if not easy_apply_button:
                prYellow(f"🥳 Already applied! Job: {job_url}")
                return True

            time.sleep(1)

            if self._complete_application_process():
                prGreen(f"✅ Successfully applied to: {job_url}")
                return True
            else:
                prRed(f"❌ Failed to apply to: {job_url}")
                return False

        except Exception as e:
            prRed(f"Error during application process: {str(e)}")
            return False

    def _find_easy_apply_button(self):
        """Find the Easy Apply button using XPath"""
        script = """
        (function() {
            const button = document.querySelector('div.jobs-apply-button--top-card button.jobs-apply-button');
            if (button) {
                button.click();
                return true;
            }
            return false;
        })()
        """
        result = self.tab.Runtime.evaluate(expression=script, returnByValue=True)
        return result.get('result', {}).get('value', False)

    def _complete_application_process(self):
        """Complete the multi-step application process"""
        max_attempts = 10
        attempt = 0

        while attempt < max_attempts:
            try:
                self._handle_application_form()
                time.sleep(random.uniform(0.1, constants.botSpeed))
                
                if not self._find_continue_button():
                    prRed("❌ No continue button")
                    if not self._find_review_button():
                        prRed("❌ No review button")
                        if not self._find_submit_button():
                            prRed("❌ No submit button")
                attempt += 1
            except Exception as e:
                prRed(f"Error in application step: {str(e)}")
                break

        try:
            submit_btn = self._find_submit_button()
            if submit_btn:
                time.sleep(random.uniform(0.1, constants.botSpeed))
                self._click_element(submit_btn)
                return True
        except:
            pass
        return False

    def _handle_application_form(self):
        """Handle the job application form"""
        time.sleep(random.uniform(0.1, constants.botSpeed * 2))
        
        # Handle other text inputs
        self._handle_text_inputs()
        
        self._handle_toronto_location()
        # Handle radio buttons and checkboxes
        self.handle_fieldset()
        
        # Handle select fields
        self._handle_select_fields()
        
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
            prRed(f"❌ Error handling fieldsets: {result_value.get('error', 'Unknown error')}")
            return False
            
        results = result_value.get('results', [])
        prGreen(f"✅ Processed {len(results)} fieldsets")
        
        return True

    def _handle_text_inputs(self):
        """Handle text input fields"""
        script = """
        (function() {
            const input_responses = {
                'linkedin': 'https://www.linkedin.com/in/leon-yao/',
                'github': 'https://github.com/leon-yao',
                'website': 'https://leoncyao.github.io/blog/',
                'phone': '6479550188',
                'email': 'leoncyao@gmail.com',
                'current,company': 'Instacart',
                'notice,period': '2 weeks',
                'salary': '100000',
                'hear': 'LinkedIn',
                'first': 'Leon',
                'last': 'Yao',
                'name': 'Leon Yao'
            };

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
                return {
                    id: input.id,
                    name: input.name,
                    placeholder: input.placeholder,
                    value: input.value,
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
            prRed(f"❌ Error handling text inputs: {result_value.get('error', 'Unknown error')}")
            return False
            
        results = result_value.get('results', [])
        prGreen(f"✅ Processed {len(results)} text input fields")
        
        return True

    def _handle_select_fields(self):
        """Handle select/dropdown fields"""
        script = """
        Array.from(document.querySelectorAll('select')).map(select => {
            select.selectedIndex = 1;
            select.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        });
        """
        self.tab.Runtime.evaluate(expression=script)

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
            prRed(f"❌ Error handling textareas: {result_value.get('error', 'Unknown error')}")
            return False
            
        results = result_value.get('results', [])
        prGreen(f"✅ Processed {len(results)} textarea fields")
        
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
            prRed(f"❌ Error logging question: {str(e)}")

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

            const locationInput = dialog.querySelector('input[id*="location-GEO-LOCATION"]');
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
            prRed(f"❌ Error inserting Toronto: {result_value.get('error', 'Unknown error')}")
            return False
            
        # Wait for suggestions
        time.sleep(2)
        
        # Second command: Press down arrow
        down_script = """
        (function() {
            const dialog = document.querySelector("[data-test-modal-id='easy-apply-modal']");
            const locationInput = dialog.querySelector('input[id*="location-GEO-LOCATION"]');
            
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
            prRed("❌ Error pressing down arrow")
            return False
            
        # Wait a bit
        time.sleep(1)
        
        # Third command: Press enter
        enter_script = """
        (function() {
            const dialog = document.querySelector("[data-test-modal-id='easy-apply-modal']");
            const locationInput = dialog.querySelector('input[id*="location-GEO-LOCATION"]');
            
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
            prRed("❌ Error pressing enter")
            return False
            
        prGreen(f"✅ Set location to: {result_value.get('value', '')}")
        return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Apply to a specific LinkedIn job using PyChrome')
    parser.add_argument('--url', required=True, help='LinkedIn job URL to apply to')
    parser.add_argument('--debug-url', default="http://localhost:9222", 
                      help='Chrome DevTools debugging URL (default: http://localhost:9222)')
    
    args = parser.parse_args()
    
    applier = PyChromeJobApplier(debugging_url=args.debug_url)
    try:
        applier.apply_to_job(args.url)
    except Exception as e:
        print(f"error {e}")