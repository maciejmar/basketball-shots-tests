import unittest
import time
import random
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
from appium.options.android import UiAutomator2Options

# --- Configuration ---
DEVICE_UDID = "R5CXC0CHHWY"            # Your device UDID
BASKETBALL_SHOTS_PACKAGE = "com.basketballshots.app"
BASKETBALL_SHOTS_ACTIVITY = ".MainActivity"
APPIUM_SERVER_URL = "http://localhost:4723"

# --- Appium Options ---
options = UiAutomator2Options()
options.udid = DEVICE_UDID
options.app_package = BASKETBALL_SHOTS_PACKAGE
options.app_activity = BASKETBALL_SHOTS_ACTIVITY
options.language = "en"
options.locale = "US"
# options.no_reset = True
# options.full_reset = False

class TestBasketballShotsLoop(unittest.TestCase):

    def setUp(self) -> None:
        """Initialize Appium driver before each test."""
        try:
            print(f"Connecting to Appium at {APPIUM_SERVER_URL} on device {DEVICE_UDID}…")
            self.driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
            print("Appium session started.")
        except Exception as e:
            print("ERROR during setup:", e)
            raise

    def tearDown(self) -> None:
        """Quit Appium driver after each test."""
        if self.driver:
            print("Quitting Appium session…")
            self.driver.quit()
        else:
            print("No Appium session to quit.")

    def test_loop_play_and_restart(self) -> None:
        """
        Repeatedly:
          1) Click Play
          2) Click the last top button (Quit)
          3) Scroll & click "Return to Menu"
          4) Wait 30s for ad to play
          5) Quit the app
          6) Relaunch the app
          7) Pause randomly between 1 and 40 seconds before next iteration
        """
        play_locator = (AppiumBy.XPATH, '//android.widget.Button[@text="Play"]')
        scroll_to_return = (
            'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
            '.scrollIntoView(new UiSelector().text("Return to Menu").instance(0));'
        )

        # initial pause for app launch
        print("Waiting 5s for app to load…")
        time.sleep(5)

        iteration = 1
        while True:
            print(f"\n=== Iteration {iteration}: Starting game session ===")

            # 1) Click Play
            print("Waiting for Play button…")
            play_btn = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(play_locator),
                "Play button not clickable"
            )
            print("Clicking Play…")
            play_btn.click()
            time.sleep(5)

            # 2) Click the last of the top buttons (Quit)
            print("Finding all android.widget.Button elements…")
            buttons = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.Button")
            if not buttons:
                self.fail("No buttons found to click after Play.")
            print(f"Clicking button #{len(buttons)} (last)…")
            buttons[-1].click()
            time.sleep(2)

            # 3) Scroll to and click "Return to Menu"
            print("Scrolling to 'Return to Menu'…")
            return_btn = self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                scroll_to_return
            )
            print("Clicking 'Return to Menu'…")
            return_btn.click()
            time.sleep(2)

            # 4) Wait for ad playback
            print("Waiting 30s for ad to play…")
            time.sleep(30)

            # 5) Quit the app
            print("Terminating the app…")
            self.driver.terminate_app(BASKETBALL_SHOTS_PACKAGE)
            time.sleep(2)

            # 6) Relaunch the app
            print("Relaunching the app…")
            self.driver.activate_app(BASKETBALL_SHOTS_PACKAGE)
            print("Waiting 5s for app to reload…")
            time.sleep(5)

            # 7) Random pause before next iteration
            pause = random.randint(1, 40)
            print(f"Waiting random {pause}s before next iteration…")
            time.sleep(pause)

            iteration += 1

if __name__ == "__main__":
    if DEVICE_UDID == "YOUR_DEVICE_UDID":
        print("ERROR: Please set your DEVICE_UDID before running.")
    else:
        unittest.main()
