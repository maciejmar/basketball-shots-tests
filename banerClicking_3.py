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
BASKETBALL_SHOTS_PACKAGE  = "com.basketballshots.app"
BASKETBALL_SHOTS_ACTIVITY = ".MainActivity"
APPIUM_BASE_PORT          = 4723
PARALLEL_OFFSET           = 2
SYSTEM_PORT_BASE          = 8200


def get_connected_devices():
    raw   = subprocess.check_output(["adb", "devices"], text=True)
    lines = raw.strip().splitlines()[1:]
    return [l.split()[0] for l in lines
            if len(l.split()) == 2 and l.split()[1] == "device" and not l.startswith("emulator-")]


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
    opts.udid         = udid
    opts.app_package  = BASKETBALL_SHOTS_PACKAGE
    opts.app_activity = BASKETBALL_SHOTS_ACTIVITY
    opts.language     = "en"
    opts.locale       = "US"
    opts.set_capability("systemPort", system_port)

    print(f"[{udid}] → Starting Appium session at {server_url}")
    try:
        driver = webdriver.Remote(server_url, options=opts)
    except WebDriverException as e:
        print(f"[{udid}] ERROR starting session: {e}")
        return

    try:
        time.sleep(1)  # let the app stabilize
        iteration = 1
        while True:
            print(f"[{udid}] === Iteration #{iteration} ===")

            # 1) Tap Change Teams
            try:
                WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable(
                        (AppiumBy.XPATH, '//android.widget.Button[@text="Change Teams"]')
                    )
                ).click()
                print(f"[{udid}] → Clicked 'Change Teams'")
            except TimeoutException:
                print(f"[{udid}] ERROR: 'Change Teams' not found")

            # 2) Scroll to bottom
            try:
                driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
                    '.scrollToEnd(5);'
                )
                print(f"[{udid}] → Scrolled to bottom")
            except Exception as e:
                print(f"[{udid}] WARNING: scroll failed: {e}")

            # 3) Tap at center-X, 20px up from bottom via W3C tap
            # 3) Tap banner area
            try:
                size = driver.get_window_size()
                x = int(size['width'] * 0.5)
                y = int(size['height'] - 20)
                driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
                print(f"[{udid}] → clickGesture at ({x},{y})")
            except Exception as e:
                print(f"[{udid}] ERROR: clickGesture failed: {e}")

            # 4) Wait
            time.sleep(2)

            # 5) Quit & relaunch
            try:
                driver.terminate_app(BASKETBALL_SHOTS_PACKAGE)
                time.sleep(1)
                driver.activate_app(BASKETBALL_SHOTS_PACKAGE)
                print(f"[{udid}] → Relaunched app")
            except Exception as e:
                print(f"[{udid}] ERROR relaunching app: {e}")

            # 6) Small random pause
            wait_time = random.randint(1,4)
            print(f"[{udid}] → Sleeping {wait_time}s before next loop\n")
            time.sleep(wait_time)
            iteration += 1

    except Exception as e:
        print(f"[{udid}] UNEXPECTED ERROR: {e}")
    finally:
        print(f"[{udid}] ← Quitting session")
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    devices = get_connected_devices()
    if not devices:
        print("No devices connected.")
        sys.exit(1)

    # Launch Appium servers
    servers = []
    for i, udid in enumerate(devices):
        port = APPIUM_BASE_PORT + i * PARALLEL_OFFSET
        p = start_appium_server(port)
        servers.append(p)
        print(f"Started Appium on port {port} for {udid}")
    time.sleep(5)

    # Spawn workers
    workers = []
    for i, udid in enumerate(devices):
        port       = APPIUM_BASE_PORT + i * PARALLEL_OFFSET
        systemPort = SYSTEM_PORT_BASE + i
        p = multiprocessing.Process(
            target=run_loop_on,
            args=(udid, port, systemPort),
            daemon=True
        )
        p.start()
        workers.append(p)

    # Graceful shutdown
    def shutdown(sig, frame):
        print("Shutting down…")
        for w in workers: w.terminate()
        for s in servers: s.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    for w in workers:
        w.join()
