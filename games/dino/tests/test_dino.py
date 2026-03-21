"""
小恐龙游戏 Selenium 测试
"""
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=390,844')
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()


@pytest.fixture
def game_url(driver):
    return "file:///Users/njh/.qclaw/workspace/games/dino/index.html"


class TestDinoGame:
    def test_page_loads(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.3)
        assert "小恐龙" in driver.title

    def test_buttons_and_canvas_exist(self, driver, game_url):
        driver.get(game_url)
        assert driver.find_element(By.TAG_NAME, "canvas") is not None
        assert driver.find_element(By.ID, "startBtn") is not None
        assert driver.find_element(By.ID, "pauseBtn") is not None
        assert driver.find_element(By.ID, "restartBtn") is not None

    def test_start_button_icon_and_feedback_style(self, driver, game_url):
        driver.get(game_url)
        icon = driver.execute_script("return document.getElementById('startBtn').textContent.trim();")
        src = driver.page_source
        assert icon == "▶"
        assert ".btn:active" in src

    def test_start_sets_running(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.2)
        driver.find_element(By.ID, "startBtn").click()
        time.sleep(0.2)
        state = driver.execute_script("return {running, paused}")
        assert state["running"] == 1
        assert state["paused"] == 0

    def test_restart_resets_state(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.2)
        driver.find_element(By.ID, "startBtn").click()
        time.sleep(0.3)
        driver.execute_script("score = 200; dinoY = 80;")
        driver.find_element(By.ID, "restartBtn").click()
        time.sleep(0.2)
        state = driver.execute_script("return {running, paused, score, dinoY}")
        assert state["running"] == 0
        assert state["paused"] == 0
        assert state["score"] == 0
        assert state["dinoY"] == 148
