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
APPIUM_BASE_PORT         = 4723
PARALLEL_OFFSET          = 2
SYSTEM_PORT_BASE         = 8200


def get_connected_devices():
    raw   = subprocess.check_output(["adb", "devices"], text=True)
    lines = raw.strip().splitlines()[1:]
    return [l.split()[0] for l in lines if "device" in l and not l.startswith("emulator-")]


def start_appium_server(port):
    cmd = ["appium", "-p", str(port), "--session-override"]
    return subprocess.Popen(cmd,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            shell=(sys.platform=="win32"))


def run_loop_on(udid, server_port, system_port):
    server_url = f"http://localhost:{server_port}"
    opts = UiAutomator2Options()
    opts.udid = udid
    opts.app_package = BASKETBALL_SHOTS_PACKAGE
    opts.app_activity = BASKETBALL_SHOTS_ACTIVITY
    opts.set_capability("systemPort", system_port)
    driver = webdriver.Remote(server_url, options=opts)
    try:
        time.sleep(1)
        iteration = 1
        while True:
            print(f"[{udid}] ■ Iteration {iteration}")

            # 1) tap Change Teams
            try:
                btn = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable(
                        (AppiumBy.XPATH, '//android.widget.Button[@text="Change Teams"]')
                    )
                )
                btn.click()
                print(f"[{udid}] → Tapped Change Teams")
            except TimeoutException:
                print(f"[{udid}] !! couldn’t find Change Teams")

            # 2) scroll to bottom
            try:
                driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
                    '.scrollToEnd(5);'
                )
                print(f"[{udid}] → Scrolled to bottom")
            except Exception as e:
                print(f"[{udid}] !! scroll failed: {e}")

            # 3) switch into WebView & dump source
            web_ctxs = driver.contexts
            print(f"[{udid}] contexts = {web_ctxs}")
            try:
                webview = next(c for c in web_ctxs if "WEBVIEW" in c)
                driver.switch_to.context(webview)
                print(f"[{udid}] → switched to {webview}")
            except StopIteration:
                print(f"[{udid}] !! no WEBVIEW context found")
                driver.switch_to.context("NATIVE_APP")
                continue

            # Debug: dump HTML so you can copy the real ad selector
            page = driver.page_source
            print(f"[{udid}] page_source snippet:\n{page[0:500]}...\n")

            # 4) find some ad element (example: ins.adsbygoogle, iframe[src*='ads'], div[class*='ad'])
            ad_selectors = [
                (AppiumBy.CSS_SELECTOR, "ins.adsbygoogle"),
                (AppiumBy.CSS_SELECTOR, "iframe[src*='ad']"),
                (AppiumBy.CSS_SELECTOR, "div[class*='ad']"),
                (AppiumBy.XPATH, "//iframe"),
                (AppiumBy.XPATH, "//*[contains(@class,'ad')]"),
            ]
            clicked = False
            for by, sel in ad_selectors:
                try:
                    el = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((by, sel))
                    )
                    el.click()
                    print(f"[{udid}] → clicked ad with {by}={sel}")
                    clicked = True
                    break
                except Exception:
                    pass
            if not clicked:
                print(f"[{udid}] !! no ad element matched any selector")

            # 5) switch back
            driver.switch_to.context("NATIVE_APP")

            # 6) small random pause
            wait = random.randint(2,5)
            print(f"[{udid}] → sleeping {wait}s\n")
            time.sleep(wait)
            iteration += 1

    finally:
        driver.quit()



if __name__ == "__main__":
    devices = get_connected_devices()
    if not devices:
        print("No devices attached.")
        sys.exit(1)

    # launch Appium servers
    servers = []
    for i,udid in enumerate(devices):
        port = APPIUM_BASE_PORT + i * PARALLEL_OFFSET
        p = start_appium_server(port)
        servers.append(p)
        print(f"  • Appium@{port} for {udid}")

    time.sleep(5)  # give servers time

    # spawn workers
    procs = []
    for i,udid in enumerate(devices):
        port       = APPIUM_BASE_PORT + i * PARALLEL_OFFSET
        systemPort = SYSTEM_PORT_BASE + i
        p = multiprocessing.Process(
            target=run_loop_on,
            args=(udid, port, systemPort),
            daemon=True
        )
        p.start()
        procs.append(p)

    # handle shutdown
    def _shutdown(sig, frame):
        print("Shutting down…")
        for p in procs: p.terminate()
        for s in servers: s.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    for p in procs: p.join()
