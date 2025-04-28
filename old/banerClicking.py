import subprocess
import multiprocessing
import time
import random
import signal
import sys
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from appium.options.android import UiAutomator2Options

# --- Configuration ---
BASKETBALL_SHOTS_PACKAGE = "com.basketballshots.app"
BASKETBALL_SHOTS_ACTIVITY = ".MainActivity"
APPIUM_BASE_PORT = 4723         # First Appium server port
PARALLEL_OFFSET = 2             # Port increment per device
SYSTEM_PORT_BASE = 8200         # Base for systemPort capability
# Replace with your actual banner-ad resource-id or other locator
BANNER_AD_ID = "com.basketballshots.app:id/bannerAd"  


def get_connected_devices():
    raw = subprocess.check_output(["adb", "devices"], text=True)
    lines = raw.strip().splitlines()[1:]
    udids = []
    for line in lines:
        parts = line.split()
        if len(parts) == 2 and parts[1] == "device" and not parts[0].startswith("emulator-"):
            udids.append(parts[0])
    return udids


def start_appium_server(port):
    cmd = ["appium", "-p", str(port), "--session-override"]
    return subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=(sys.platform == "win32")
    )


def run_loop_on(udid, server_port, system_port):
    server_url = f"http://localhost:{server_port}"
    opts = UiAutomator2Options()
    opts.udid = udid
    opts.app_package = BASKETBALL_SHOTS_PACKAGE
    opts.app_activity = BASKETBALL_SHOTS_ACTIVITY
    opts.language = "en"
    opts.locale = "US"
    opts.set_capability("systemPort", system_port)

    print(f"[{udid}] → Starting Appium session at {server_url} (systemPort={system_port})")
    try:
        driver = webdriver.Remote(server_url, options=opts)
    except WebDriverException as e:
        print(f"[{udid}] ERROR starting session: {e}")
        return

    try:
        time.sleep(1)
        iteration = 1
        while True:
            print(f"[{udid}] Iteration #{iteration}")

            # 1) Click Change Teams
            try:
                change_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable(
                        (AppiumBy.XPATH, '//android.widget.Button[@text="Change Teams"]')
                    )
                )
                change_btn.click()
                print(f"[{udid}] Clicked 'Change Teams'")
            except TimeoutException:
                print(f"[{udid}] ERROR: 'Change Teams' button not found.")
                # still attempt scroll/ad-click or skip?
            
            # 2) Scroll to bottom of the screen
            try:
                driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
                    '.scrollToEnd(5);'
                )
                print(f"[{udid}] Scrolled to bottom")
            except Exception as e:
                print(f"[{udid}] WARNING: could not scroll to bottom: {e}")

            # 3) Click the banner ad
            try:
                banner = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((AppiumBy.ID, BANNER_AD_ID))
                )
                banner.click()
                print(f"[{udid}] Clicked banner ad")
            except TimeoutException:
                print(f"[{udid}] ERROR: banner ad not found by ID '{BANNER_AD_ID}'")
            except Exception as e:
                print(f"[{udid}] ERROR clicking banner ad: {e}")

            # 4) Random pause before next iteration
            wait_time = random.randint(2, 5)
            print(f"[{udid}] Waiting {wait_time}s before next iteration...")
            time.sleep(wait_time)

            iteration += 1

    except Exception as e:
        print(f"[{udid}] UNEXPECTED ERROR: {e}")
    finally:
        print(f"[{udid}] ← Quitting session")
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    devices = get_connected_devices()
    if not devices:
        print("No physical devices found. Connect devices and retry.")
        sys.exit(1)

    # Launch Appium servers
    appium_processes = []
    for idx, udid in enumerate(devices):
        port = APPIUM_BASE_PORT + idx * PARALLEL_OFFSET
        p = start_appium_server(port)
        appium_processes.append(p)
        print(f"Spawned Appium server on port {port} for device {udid}")

    time.sleep(5)  # allow servers to boot

    # Spawn worker processes
    workers = []
    for idx, udid in enumerate(devices):
        port = APPIUM_BASE_PORT + idx * PARALLEL_OFFSET
        system_port = SYSTEM_PORT_BASE + idx
        p = multiprocessing.Process(
            target=run_loop_on,
            args=(udid, port, system_port),
            daemon=True
        )
        p.start()
        workers.append(p)
        print(f"Spawned worker for {udid} → Appium port {port}, systemPort {system_port}")

    # Graceful shutdown
    def shutdown(signum, frame):
        print("Shutting down workers and Appium servers...")
        for w in workers:
            w.terminate()
        for a in appium_processes:
            a.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)

    # Keep main alive
    for w in workers:
        w.join()
