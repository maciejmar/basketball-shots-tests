import unittest
import time # Import time for pauses
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from appium.options.android import UiAutomator2Options # Use this specifically for Android + uiautomator2

# --- Configuration ---
# !!! Replace with your actual device ID from 'adb devices' !!!
DEVICE_UDID = "R5CXC0CHHWY"
# These are common, but verify with 'adb shell dumpsys window | findstr mCurrentFocus' if needed
SETTINGS_PACKAGE = 'com.android.settings'
SETTINGS_ACTIVITY = '.Settings' # Or the specific activity like 'com.android.settings.Settings'

# Verify this text on your device using Appium Inspector or manually
BATTERY_TEXT = 'Battery'

APPIUM_SERVER_URL = 'http://localhost:4723'
# --- End Configuration ---

# Import the Options class


# ...

# --- Define Capabilities using Options Object ---
options = UiAutomator2Options()
options.udid = DEVICE_UDID
options.app_package = SETTINGS_PACKAGE
options.app_activity = SETTINGS_ACTIVITY
options.language = 'en'
options.locale = 'US'
# options.no_reset = True
# --- End Options Object ---
class TestRootedAppium(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = None
        try:
            print(f"Connecting to Appium server at {APPIUM_SERVER_URL} for device {DEVICE_UDID}...")
            self.driver = webdriver.Remote(APPIUM_SERVER_URL, options=options) # Using Options object
            print("Session created successfully.")
            # ...
        except Exception as e:
            # ... (your error reporting) ...
            pass # Or handle failure as needed

            # ... (rest of the except block is the same) ...
            print(f"\n!!!!!!!!!!!!!! ERROR DURING SETUP !!!!!!!!!!!!!!")
            print(f"Failed to create Appium session: {e}")
            print("Please check:")
            print("1. Is the Appium server running?")
            print("2. Is the device connected via USB and authorized (`adb devices`)?")
            print(f"3. Is the UDID '{DEVICE_UDID}' correct?")
            print("4. Are the Appium server logs showing any errors?")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    def tearDown(self) -> None:
        if self.driver:
            print("Quitting Appium session...")
            self.driver.quit()
            print("Session closed.")
        else:
            print("No active session to quit.")
    def test_settings_and_root_command(self) -> None:
        # --- Check if driver initialized (already there) ---
        if not self.driver:
            self.skipTest("Skipping test because Appium driver failed to initialize in setUp.")
            return # Use return for clarity

        print("\n--- Starting Test: Settings Interaction and Root Command ---")

        try:
            # Use a reasonable wait time for finding elements, including after scrolling
            wait = WebDriverWait(self.driver, 20) # Increased timeout slightly to account for scrolling time

            # --- ADD SCROLLING LOGIC ---
            print(f"Attempting to scroll down until '{BATTERY_TEXT}' element is found...")

            # 1. Identify the scrollable container
            # In Settings, the main list is often a ScrollView or a descendant within a FrameLayout
            # You might need to inspect the app's layout (using Appium Inspector) to find the correct one.
            # Common candidates are: "//android.widget.ScrollView", "//android.widget.ListView",
            # or sometimes just scrolling the root element "//*" works.
            # Let's try a common one like ScrollView, or the root element as a fallback.
            # You can find the actual element id/xpath using Appium Inspector.
            scrollable_container_xpath = "//android.widget.ScrollView"
            # As a fallback, you might scroll the root layout
            # scrollable_container_xpath = "//android.widget.FrameLayout" # Or other root layout

            # Find the scrollable element (optional, but good practice)
            # If this fails, try scrolling the whole screen by removing elementId from execute_script
            try:
                scrollable_element = wait.until(
                    EC.presence_of_element_located((AppiumBy.XPATH, scrollable_container_xpath)),
                    "Could not find scrollable container element"
                )
                scrollable_element_id = scrollable_element.id
                print(f"Found scrollable container using XPath: {scrollable_container_xpath}")
            except TimeoutException:
                print(f"WARN: Could not find scrollable container {scrollable_container_xpath}. Attempting to scroll the entire screen.")
                scrollable_element_id = None # Will scroll the entire viewport

            # 2. Execute the 'mobile: scroll' command
            # We use the Android UiSelector strategy to find the element by text while scrolling
            self.driver.execute_script('mobile: scroll', {
                'elementId': scrollable_element_id, # Pass the ID if a container was found (can be None)
                'direction': 'down', # Or 'up', 'left', 'right'
                # --- CHANGE THIS LINE ---
                # Original: 'strategy': 'uiautomator',
                'strategy': '-android uiautomator', # Use the correct strategy name listed in the error
                # --- END CHANGE ---
                'selector': f'new UiSelector().text("{BATTERY_TEXT}")', # UiSelector command to find the element
                'maxScrolls': 10 # Optional: Maximum number of scrolls to attempt. Prevent infinite loops.
            })

            print(f"Scrolling command executed. Element '{BATTERY_TEXT}' should now be in view.")
            time.sleep(1) # Give the UI a moment to settle after scrolling

            # --- Now find and click the "Battery" element (it should be visible now) ---
            battery_element_xpath = f'//*[@text="{BATTERY_TEXT}"]'
            print(f"Verifying and clicking element with text: '{BATTERY_TEXT}' after scrolling...")

            # Use visibility_of_element_located now, as we expect it to be visible
            battery_element = wait.until(
                EC.visibility_of_element_located((AppiumBy.XPATH, battery_element_xpath)),
                f"Element with text '{BATTERY_TEXT}' not visible after scrolling."
            )
            print("Battery element found and is visible. Clicking...")
            battery_element.click()
            print("Clicked Battery element. Pausing for 2 seconds...")
            time.sleep(2) # Pause so you can see the Battery screen

            # --- Rest of your test (Execute a root command) ---
            # ... (Your existing code for force-stopping the app) ...
            target_package = SETTINGS_PACKAGE
            print(f"Executing root command to force-stop package: {target_package}")
            
            
            # ... Code before executing the shell command ...

            # 2. Execute a root command to force-stop the Settings app
            target_package = SETTINGS_PACKAGE
            print(f"Executing root command to force-stop package: {target_package}")

            # Construct the shell command arguments for 'mobile: shell'
            command_args = {'command': 'su', 'args': ['-c', f'am force-stop {target_package}']} # <-- command_args is defined here

            # Execute the command
            print("Executing root command...") # <-- This print is from the new block
            result = self.driver.execute_script('mobile: shell', command_args) # <-- FIRST EXECUTION using command_args defined above

            print("Shell command executed.") # <-- This print is from the new block

            # --- Handle the result which might be a dict or a string ---
            if isinstance(result, dict):
                # Expected format: dictionary with stdout and stderr
                stdout = result.get('stdout', 'N/A')
                stderr = result.get('stderr', 'N/A')
                print(f"Result (stdout): {stdout}")
                if stderr and stderr != 'N/A':
                    print(f"WARNING: Shell command produced error output (stderr): {stderr}")
                elif isinstance(result, str):
                # Handle case where result is just the stdout string
                    print(f"Result (plain stdout string): {result}")
                    stderr = None # Assume no separate stderr if it's just a string
                else:
                # Handle unexpected result types
                    print(f"WARNING: Shell command returned unexpected type ({type(result)}). Full result: {result}")
                    stderr = None # Assume no separate stderr
                    # --- End result handling ---

                # The following line assumes the command itself succeeded if we got this far
                print(f"Successfully processed result for force-stop command.") # <-- This print is from the new block

        
                print("Pausing for 3 seconds to observe...") # <-- Add the final pause here
                time.sleep(1)

            # ... Rest of the test method (except blocks) ...
            
            
            # Execute the command
            print("Executing root command...")
            result = self.driver.execute_script('mobile: shell', command_args)

            print("Shell command executed.")

            # --- Handle the result which might be a dict or a string ---
            if isinstance(result, dict):
            # Expected format: dictionary with stdout and stderr
                stdout = result.get('stdout', 'N/A')
                stderr = result.get('stderr', 'N/A')
                print(f"Result (stdout): {stdout}")
                if stderr and stderr != 'N/A':
                    print(f"WARNING: Shell command produced error output (stderr): {stderr}")
                    # Optional: fail the test if stderr is present and indicates failure
                    # if "some error indicator" in stderr:
                    #     self.fail(f"Root command failed with stderr: {stderr}")

                elif isinstance(result, str):
                # Handle case where result is just the stdout string
                    print(f"Result (plain stdout string): {result}")
                    stderr = None # Assume no separate stderr if it's just a string

            else:
                # Handle unexpected result types
                print(f"WARNING: Shell command returned unexpected type ({type(result)}). Full result: {result}")
                stderr = None # Assume no separate stderr

            # --- End result handling ---

            # The following line assumes the command itself succeeded if we got this far
            print(f"Successfully processed result for force-stop command.") # Changed message slightly
            
            


        except TimeoutException as e:
            # Catch TimeoutException specifically for the WebDriverWait
            print(f"ERROR: Timed out: {e}") # Print the specific message from the exception
            # The error message within the exception will indicate which wait failed (scrollable container or battery element)
            self.fail(f"Test failed: Element not found or visible after scrolling. {e}")
        except NoSuchElementException as e:
            # Catch NoSuchElementException if an element isn't found at all (less likely with scrolling logic, but possible)
            print(f"ERROR: Element not found: {e}")
            self.fail(f"Test failed: Element not found after attempting to scroll. {e}")
        except Exception as e:
            # Catch any other unexpected errors
            print(f"An unexpected error occurred during the test: {e}")
            # Optional: save screenshot on error
            try:
                self.driver.save_screenshot("error_screenshot.png")
                print("Saved screenshot to error_screenshot.png")
            except Exception as screenshot_error:
                print(f"Could not save screenshot: {screenshot_error}")
            self.fail(f"Test failed due to an exception: {e}")

        print("--- Test Completed ---")



#         print("--- Test Completed ---")

if __name__ == '__main__':
    # Make sure to replace 'YOUR_DEVICE_UDID' above before running
    if DEVICE_UDID == 'YOUR_DEVICE_UDID':
         print("\n*** PLEASE REPLACE 'YOUR_DEVICE_UDID' in the script with your actual device ID! ***\n")
    else:
        unittest.main()