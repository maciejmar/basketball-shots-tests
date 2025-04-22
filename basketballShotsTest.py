import unittest
import time # Import time for pauses
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException # Import WebDriverException for broader Appium errors
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By # For web locators
# --- Configuration ---
DEVICE_UDID = "R5CXC0CHHWY" # Your device UDID

# --- NEW APP CONFIGURATION ---
# !!! REPLACE THESE WITH YOUR ACTUAL APP PACKAGE AND ACTIVITY FOUND using adb dumpsys !!!
BASKETBALL_SHOTS_PACKAGE = 'com.basketballshots.app' # <-- REPLACE THIS!
BASKETBALL_SHOTS_ACTIVITY = '.MainActivity' # <-- REPLACE THIS! (Keep the dot if it starts with one)
# --- END NEW APP CONFIGURATION ---

# Original Settings config (can keep for reference or remove if not needed)
SETTINGS_PACKAGE = 'com.android.settings'
SETTINGS_ACTIVITY = '.Settings'
BATTERY_TEXT = 'Battery' # Specific to Settings app

APPIUM_SERVER_URL = 'http://localhost:4723'
# --- End Configuration ---

# --- Define Capabilities using Options Object (NOW TARGETING BASKETBALL SHOTS) ---
options = UiAutomator2Options()
options.udid = DEVICE_UDID
options.app_package = BASKETBALL_SHOTS_PACKAGE # Use the new package variable
options.app_activity = BASKETBALL_SHOTS_ACTIVITY # Use the new activity variable
options.language = 'en' # Keep or change as needed
options.locale = 'US' # Keep or change as needed
# options.no_reset = True # Set to True if you DON'T want the app data reset on each run
# options.full_reset = False # Often used with no_reset=False
# --- End Options Object ---


class TestBasketballShots(unittest.TestCase): # Renamed the class for clarity

    def setUp(self) -> None:
        self.driver = None
        try:
            print(f"Connecting to Appium server at {APPIUM_SERVER_URL} for device {DEVICE_UDID}...")
            # The options object defined globally is used here
            self.driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
            print("Session created successfully.")
            # Set a global implicit wait if desired, though explicit waits are generally better
            # self.driver.implicitly_wait(10)
        except Exception as e: # Catch all exceptions during setup
            print(f"\n!!!!!!!!!!!!!! ERROR DURING SETUP !!!!!!!!!!!!!!")
            print(f"Failed to create Appium session: {e}")
            print("Please check:")
            print("1. Is the Appium server running (with --allow-insecure adb_shell)?")
            print("2. Is the device connected via USB and authorized (`adb devices`)?")
            print(f"3. Is the UDID '{DEVICE_UDID}' correct?")
            print("4. Are the Appium server logs showing any errors during connection?")
            print(f"5. Are the App Package ('{BASKETBALL_SHOTS_PACKAGE}') and Activity ('{BASKETBALL_SHOTS_ACTIVITY}') correct in the script?")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")


    def tearDown(self) -> None:
        if self.driver:
            print("Quitting Appium session...")
            self.driver.quit()
            print("Session closed.")
        else:
            print("No active session to quit.")

    # Rename the test method to reflect the new app
    def test_basketball_shots_launch_and_stop(self) -> None:
        # --- Check if driver initialized (already there) ---
        if not self.driver:
            self.skipTest("Skipping test because Appium driver failed to initialize in setUp.")
            return # Use return for clarity

        print("\n--- Starting Test: Basketball Shots Launch and Stop ---")

        try:
            # 1. The app 'basketballShots' will be launched automatically by Appium because of the capabilities in setUp.
            print(f"App '{BASKETBALL_SHOTS_PACKAGE}' should be launched by Appium session creation. Pausing for 5 seconds to let it load...")
            time.sleep(5) # Give the app time to fully load
            
            
             # --- START OF NEW CODE ADDED FOR PLAY BUTTON CLICK ---
            print("Attempting to find and click the 'Play' button...")

            # --- Replace the LOCATOR STRATEGY and LOCATOR VALUE below based on Appium Inspector ---
            # Example using XPath (adjust as needed)
            play_button_locator = (AppiumBy.XPATH, '//android.widget.Button[@text="Play"]')
            # --- END Replace LOCATOR ---

            # Use WebDriverWait to wait for the button to be visible and clickable
            # Use a separate wait variable or the existing 'wait' if its timeout is sufficient (20s)
            wait = WebDriverWait(self.driver, 10) # Shorter wait for element interaction
            print(f"Waiting for Play button using locator: {play_button_locator}...")

            play_button = wait.until(
                 EC.element_to_be_clickable(play_button_locator), # Wait until the element is clickable
                 "Play button not found or not clickable within timeout" # Message if wait fails
              )

            print("Play button found. Clicking...")
            play_button.click() # Perform the click action
            print("Play button clicked. Pausing for 2 seconds...")
            time.sleep(2) # Pause to see the result of the click
            # --- END OF NEW CODE ADDED FOR PLAY BUTTON CLICK ---
            
            # --- REPLACE THE ENTIRE WEBVIEW CHECK/SWITCH BLOCK BELOW THIS LINE ---
            # ...
            # print("Attempting to interact with element in Webview (Quit button)...") # <- This print starts the old block
            # print("Checking available contexts...") # <- This is in the old block
            # contexts = self.driver.contexts
            # ... (all the context checking, switching, and webview finding logic) ...
            # --- WITH THE NATIVE FINDING CODE BELOW ---


            # --- START OF NEW CODE ADDED FOR NATIVE QUIT BUTTON CLICK ---
            print("No WEBVIEW context found. Attempting to find the Quit button as a native element.")
            
            

            try:
                    # Use WebDriverWait to wait for the native button to be visible and clickable
                    # Use the existing 'wait' object if its timeout is sufficient (currently 10s, might need more?)
                    # If the button takes longer to appear, increase the timeout for 'wait' defined earlier.
                    native_wait = wait # Using the existing wait object

                    print("Attempting to find and click the native 'Quit' button...")

                    # --- Replace the NATIVE LOCATOR STRATEGY and LOCATOR VALUE below based on Appium Inspector (in NATIVE_APP context) ---
                    # YOU MUST INSPECT THE ELEMENT TO GET THE CORRECT LOCATOR.
                    # Examples:
                    # Example using Accessibility ID (if content-desc="Quit")
                    # quit_button_locator_native = (AppiumBy.ACCESSIBILITY_ID, 'Quit')
                    # Example using XPath (targeting a native element like android.widget.Button[@text="Quit"])
                    # quit_button_locator_native = (AppiumBy.XPATH, '//android.widget.Button[@text="Quit"]')
                    # Example using ID (if the button has a resource-id)
                    # quit_button_locator_native = (AppiumBy.ID, 'com.basketballshots.app:id/quit_button_id')

                    # --- REMEMBER TO REPLACE THIS WITH YOUR ACTUAL NATIVE LOCATOR ---
                    # This is just a placeholder example that likely won't work for your app:
                    quit_button_locator_native = (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Quit"]') # Example assuming alt="Quit" becomes content-desc="Quit" on an ImageView

                    print(f"Waiting for native Quit button using locator: {quit_button_locator_native}...")
                    quit_button_native = native_wait.until(
                    EC.element_to_be_clickable(quit_button_locator_native), # Wait until the native element is clickable
                    "Native Quit button not found or not clickable within timeout" # Message if wait fails
                    )
                                        

                    print("Native Quit button found. Clicking...")
                    quit_button_native.click() # Perform the click action
                    print("Native Quit button clicked. Pausing for 2 seconds...")
                    time.sleep(2) # Pause to see the result

            except TimeoutException as e:
                print(f"ERROR: Timed out waiting for Quit button in webview: {e}")
                # Re-raise the exception to be caught by the main handler
                raise # Re-raise the exception so it's caught by the main exception handler

            finally:
                # 4. Always switch back to NATIVE_APP context when done with web elements
                print("Switching back to NATIVE_APP context...")
                self.driver.switch_to.context('NATIVE_APP')
                print("Switched back to NATIVE_APP.")

        except TimeoutException:
            print(f"ERROR: Timed out waiting for native Quit button.")
            # Re-raise the exception to be caught by the main exception handler
            raise # Re-raise the exception

    


            # Example: Force-stop the application after your automation steps (Optional)
                        # ... (rest of the force-stop logic and result handling) ...

            # --- Keep the exception handling blocks (updated to catch webview errors) ---
                    # ... (TimeoutException, NoSuchElementException, WebDriverException, Exception) ...
                    # Note: The TimeoutException block was updated in the previous step to catch the webview wait timeout too
        except TimeoutException as e: # This will catch timeouts from any WebDriverWait
            print(f"ERROR: Timed out waiting for an element: {e}")
            self.fail(f"Test failed: Element not found within timeout. {e}")
        # Other exceptions remain the same

            print("--- Test Completed ---")
            time.sleep(5)
            # --- !!! IMPORTANT !!! ---
            # >>> Replace the code below this line with YOUR automation steps <<<
            # These steps will interact with the elements in your 'basketballShots' app.
            # You'll need to use Appium Inspector to find the locators (IDs, XPaths, etc.)
            # for buttons, text fields, or other elements in your app.
            # Examples:
            # button = self.driver.find_element(AppiumBy.ID, 'com.yourcompany.basketballshots:id/my_button')
            # button.click()
            # text_field = self.driver.find_element(AppiumBy.XPATH, '//android.widget.EditText[@text="Enter name"]')
            # text_field.send_keys('Test Name')
            # time.sleep(2) # Pause after actions

            print("\n>>> Add your specific 'basketballShots' automation logic here <<<")
            print(">>> (Currently just pausing and force-stopping) <<<")
            # --- !!! IMPORTANT !!! ---


            # Example: Force-stop the *new* application after your automation steps
            # If you want to force-stop your app as the last step:
            target_package = BASKETBALL_SHOTS_PACKAGE # Use the new package variable
            print(f"Executing root command to force-stop package: {target_package}")
            command_args = {'command': 'su', 'args': ['-c', f'am force-stop {target_package}']}

            print("Executing root command...")
            result = self.driver.execute_script('mobile: shell', command_args)
            print("Shell command executed.")

            # --- Handle the result (keep this logic) ---
            if isinstance(result, dict):
                stdout = result.get('stdout', 'N/A')
                stderr = result.get('stderr', 'N/A')
                print(f"Result (stdout): {stdout}")
                if stderr and stderr != 'N/A':
                    print(f"WARNING: Shell command produced error output (stderr): {stderr}")
                    # Optional: fail the test if stderr is present and indicates failure
                    # if "some error indicator" in stderr: # Add specific error checks if needed
                    #    self.fail(f"Root command failed with stderr: {stderr}")

            elif isinstance(result, str):
                print(f"Result (plain stdout string): {result}")
                # Assume no separate stderr if it's just a string
            else:
                # Handle unexpected result types
                print(f"WARNING: Shell command returned unexpected type ({type(result)}). Full result: {result}")

            print(f"Successfully processed result for force-stop command.")
            # --- End result handling ---

            print("Pausing for 3 seconds to observe...")
            time.sleep(3)

        # --- Keep the exception handling blocks ---
        except TimeoutException as e:
            # This exception is less likely now unless you add WebDriverWait for elements
            print(f"ERROR: Timed out waiting for an element: {e}")
            self.fail(f"Test failed: Element not found within timeout. {e}")
        except NoSuchElementException as e:
            # This exception occurs if find_element fails
            print(f"ERROR: Element not found: {e}")
            self.fail(f"Test failed: Element does not exist. {e}")
        except WebDriverException as e: # Catch broader WebDriver issues during test execution
            print(f"An Appium/WebDriver error occurred during the test: {e}")
            self.fail(f"Test failed due to WebDriver error: {e}")
        except Exception as e:
            # Catch any other unexpected errors
            print(f"An unexpected error occurred during the test: {e}")
            # Optional: save screenshot on error
            try:
                self.driver.save_screenshot("error_screenshot_basketball_shots.png") # Use a different name
                print("Saved screenshot to error_screenshot_basketball_shots.png")
            except Exception as screenshot_error:
                print(f"Could not save screenshot: {screenshot_error}")
            self.fail(f"Test failed due to an exception: {e}")

        print("--- Test Completed ---")


if __name__ == '__main__':
    # Make sure to replace 'YOUR_DEVICE_UDID' above before running
    if DEVICE_UDID == 'YOUR_DEVICE_UDID': # Keep this check
          print("\n*** PLEASE REPLACE 'YOUR_DEVICE_UDID' in the script with your actual device ID! ***\n")
    # You might want to add a check for the default basketball shots package too
    elif BASKETBALL_SHOTS_PACKAGE == 'com.yourcompany.basketballshots':
         print("\n*** PLEASE REPLACE 'com.yourcompany.basketballshots' and '.MainActivity' with your app's package and activity! ***\n")
    else:
        unittest.main() # Run the tests