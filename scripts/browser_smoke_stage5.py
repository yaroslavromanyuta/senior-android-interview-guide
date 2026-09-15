from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

root = Path(__file__).resolve().parents[1]
url = (root / "index.html").as_uri()
opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--window-size=1280,900")
driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 10)
results = []
try:
    driver.get(url)
    driver.execute_script("document.documentElement.style.scrollBehavior='auto'")
    uk_id = "android-background-execution"
    en_id = "en-android-background-execution"
    uk = wait.until(EC.presence_of_element_located((By.ID, uk_id)))
    assert uk.is_displayed()
    uk_link = driver.find_element(By.CSS_SELECTOR, f'a[data-target="{uk_id}"]')
    uk_link.click()
    wait.until(lambda d: d.execute_script("return location.hash") == f"#{uk_id}")
    assert uk.get_attribute("open") is not None
    results.append("UA TOC anchor")

    uk_summary = uk.find_element(By.CSS_SELECTOR, ":scope > summary")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", uk_summary)
    uk_summary.click()
    wait.until(lambda d: uk.get_attribute("open") is None)
    uk_summary.click()
    wait.until(lambda d: uk.get_attribute("open") is not None)
    results.append("UA collapsible")

    driver.find_element(By.ID, "langBtn").click()
    wait.until(lambda d: d.find_element(By.ID, en_id).is_displayed())
    assert not driver.find_element(By.ID, uk_id).is_displayed()
    assert driver.find_element(By.TAG_NAME, "html").get_attribute("lang") == "en"
    results.append("language switch UA→EN")

    en = driver.find_element(By.ID, en_id)
    en_link = driver.find_element(By.CSS_SELECTOR, f'a[data-target="{en_id}"]')
    en_link.click()
    wait.until(lambda d: d.execute_script("return location.hash") == f"#{en_id}")
    assert en.get_attribute("open") is not None
    results.append("EN TOC anchor")

    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True},
    )
    wait.until(lambda d: d.execute_script("return innerWidth === 390 && innerHeight === 844"))
    en_summary = en.find_element(By.CSS_SELECTOR, ":scope > summary")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", en_summary)
    en_summary.click()
    wait.until(lambda d: en.get_attribute("open") is None)
    en_summary.click()
    wait.until(lambda d: en.get_attribute("open") is not None)
    metrics = driver.execute_script("return {w:innerWidth, h:innerHeight, doc:document.documentElement.scrollWidth, body:document.body.scrollWidth, title:document.querySelector('#en-android-background-execution .major-title').getBoundingClientRect().width}")
    assert metrics["w"] == 390 and metrics["h"] == 844, metrics
    assert metrics["doc"] <= 390 and metrics["body"] <= 390, metrics
    results.append("mobile 390×844 no overflow + EN collapsible")

    print("Browser smoke passed: " + "; ".join(results))
finally:
    driver.quit()
