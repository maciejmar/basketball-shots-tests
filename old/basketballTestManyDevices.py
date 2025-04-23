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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from appium.options.android import UiAutomator2Options

# --- Configuration ---
BASKETBALL_SHOTS_PACKAGE = "com.basketballshots.app"
BASKETBALL_SHOTS_ACTIVITY = ".MainActivity"
APPIUM_BASE_PORT = 4723         # first Appium server port
PARALLEL_OFFSET = 2             # port increment per device
SYSTEM_PORT_BASE = 8200         # base for systemPort capability


def get_connected_devices():
    """
    Returns a list of UDIDs for all connected physical devices (not emulators).
    """
    raw = subprocess.check_output(["adb", "devices"], text=True)
    lines = raw.strip().splitlines()[1:]  # skip header
    udids = []
    for line in lines:
        parts = line.split()
        if len(parts) == 2 and parts[1] == "device" and not parts[0].startswith("emulator-"):
            udids.append(parts[0])
    return udids


def start_appium_server(port):
    """
    Spawn an Appium server on the given port.
    Returns the Popen object.
    """
    cmd = [
        "appium",
        "-p", str(port),
        "--session-override"
    ]
    return subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=(sys.platform == "win32")
    )


def run_loop_on(udid, server_port, system_port):
    """
    Connects to Appium at localhost:server_port,
    drives device udid in a play-and-restart loop using systemPort.
    """
    server_url = f"http://localhost:{server_port}"
    opts = UiAutomator2Options()
    opts.udid = udid
    opts.app_package = BASKETBALL_SHOTS_PACKAGE
    opts.app_activity = BASKETBALL_SHOTS_ACTIVITY
    opts.language = "en"
    opts.locale = "US"
    opts.set_capability("systemPort", system_port)

    print(f"[{udid}] → Starting Appium session at {server_url} (systemPort={system_port})")
    driver = webdriver.Remote(server_url, options=opts)

    try:
        # initial wait for app
        time.sleep(5)
        iteration = 1
        while True:
            print(f"[{udid}] Iteration #{iteration}")

            # 1) Click Play
            play_btn = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.Button[@text="Play"]'))
            )
            play_btn.click()
            time.sleep(5)

            # 2) Click the last button (Quit)
            buttons = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.Button")
            if not buttons:
                print(f"[{udid}] WARNING: No buttons found after Play.")
            else:
                buttons[-1].click()
            time.sleep(2)

            # 3) Scroll and click "Return to Menu"
            ui_scroll = (
                'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
                '.scrollIntoView(new UiSelector().text("Return to Menu").instance(0));'
            )
            try:
                return_btn = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, ui_scroll))
                )
                return_btn.click()
            except (TimeoutException, NoSuchElementException):
                print(f"[{udid}] ERROR: 'Return to Menu' not found. Skipping iteration.")
                iteration += 1
                continue
            time.sleep(2)

            # 4) Wait for ad playback
            time.sleep(30)

            # 5) Quit and relaunch the app
            driver.terminate_app(BASKETBALL_SHOTS_PACKAGE)
            time.sleep(2)
            driver.activate_app(BASKETBALL_SHOTS_PACKAGE)
            time.sleep(5)

            # 6) Random pause before next iteration
            wait_time = random.randint(1, 2)
            print(f"[{udid}] Waiting {wait_time}s before next iteration...")
            time.sleep(wait_time)

            iteration += 1

    except Exception as e:
        print(f"[{udid}] UNEXPECTED ERROR: {e}")
    finally:
        print(f"[{udid}] ← Quitting session")
        driver.quit()


if __name__ == "__main__":
    devices = get_connected_devices()
    if not devices:
        print("No physical devices found. Connect devices and retry.")
        sys.exit(1)

    # 1) Launch Appium servers
    appium_processes = []
    for idx, udid in enumerate(devices):
        port = APPIUM_BASE_PORT + idx * PARALLEL_OFFSET
        p = start_appium_server(port)
        appium_processes.append(p)
        print(f"Spawned Appium server on port {port} for device {udid}")

    # Give servers time to start
    time.sleep(5)

    # 2) Spawn worker processes
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

    # 3) Shutdown handling
    def shutdown(signum, frame):
        print("Shutting down workers and Appium servers...")
        for w in workers:
            w.terminate()
        for a in appium_processes:
            a.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)

    # 4) Keep main alive
    for w in workers:
        w.join()