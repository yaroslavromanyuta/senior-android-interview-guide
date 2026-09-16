#!/usr/bin/env python3
"""Headless mobile smoke test for the bilingual Stage 28 guide section."""

from __future__ import annotations

import contextlib
import http.server
import threading
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


ROOT = Path(__file__).resolve().parents[1]
UA_ID = "system-design-chat-real-time-updates"
EN_ID = "en-system-design-chat-real-time-updates"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


@contextlib.contextmanager
def loopback_server():
    handler = lambda *args, **kwargs: QuietHandler(  # noqa: E731
        *args, directory=str(ROOT), **kwargs
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/index.html"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def assert_no_horizontal_overflow(driver: webdriver.Chrome) -> dict[str, int]:
    metrics = driver.execute_script(
        "return {"
        "width: innerWidth, height: innerHeight, "
        "documentWidth: document.documentElement.scrollWidth, "
        "bodyWidth: document.body.scrollWidth"
        "}"
    )
    assert metrics["width"] == 390 and metrics["height"] == 844, metrics
    assert metrics["documentWidth"] <= 390 and metrics["bodyWidth"] <= 390, metrics
    return metrics


def open_toc_target(driver: webdriver.Chrome, wait: WebDriverWait, target_id: str) -> None:
    driver.find_element(By.ID, "menuBtn").click()
    wait.until(lambda d: "nav-open" in d.find_element(By.TAG_NAME, "body").get_attribute("class"))
    link = driver.find_element(By.CSS_SELECTOR, f'a[data-target="{target_id}"]')
    assert link.get_attribute("href").endswith(f"#{target_id}")
    driver.execute_script("arguments[0].click()", link)
    wait.until(lambda d: d.execute_script("return location.hash") == f"#{target_id}")
    wait.until(lambda d: "nav-open" not in d.find_element(By.TAG_NAME, "body").get_attribute("class"))


def toggle_section(driver: webdriver.Chrome, wait: WebDriverWait, section_id: str) -> None:
    section = driver.find_element(By.ID, section_id)
    summary = section.find_element(By.CSS_SELECTOR, ":scope > summary")
    driver.execute_script("arguments[0].click()", summary)
    wait.until(lambda d: section.get_attribute("open") is None)
    driver.execute_script("arguments[0].click()", summary)
    wait.until(lambda d: section.get_attribute("open") is not None)


def main() -> None:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=390,844")

    results: list[str] = []
    with loopback_server() as url:
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 10)
        try:
            driver.execute_cdp_cmd(
                "Emulation.setDeviceMetricsOverride",
                {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True},
            )
            driver.get(url)
            driver.execute_script("document.documentElement.style.scrollBehavior='auto'")
            wait.until(lambda d: d.find_element(By.ID, UA_ID).is_displayed())
            assert_no_horizontal_overflow(driver)

            open_toc_target(driver, wait, UA_ID)
            ua = driver.find_element(By.ID, UA_ID)
            assert ua.is_displayed() and ua.get_attribute("open") is not None
            results.append("UA anchor + TOC")

            toggle_section(driver, wait, UA_ID)
            assert_no_horizontal_overflow(driver)
            results.append("UA collapsible")

            driver.find_element(By.ID, "langBtn").click()
            wait.until(lambda d: d.find_element(By.ID, EN_ID).is_displayed())
            assert not driver.find_element(By.ID, UA_ID).is_displayed()
            assert driver.find_element(By.TAG_NAME, "html").get_attribute("lang") == "en"
            assert_no_horizontal_overflow(driver)
            results.append("language switch UA→EN")

            open_toc_target(driver, wait, EN_ID)
            en = driver.find_element(By.ID, EN_ID)
            assert en.is_displayed() and en.get_attribute("open") is not None
            results.append("EN anchor + TOC")

            toggle_section(driver, wait, EN_ID)
            metrics = assert_no_horizontal_overflow(driver)
            results.append(
                "EN collapsible + viewport "
                f"{metrics['width']}×{metrics['height']} without horizontal overflow"
            )

            print("Stage 28 browser smoke passed: " + "; ".join(results))
        finally:
            driver.quit()


if __name__ == "__main__":
    main()
