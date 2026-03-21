"""
打砖块游戏 Selenium 系统测试
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
    chrome_options.add_argument('--window-size=400,700')
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()


@pytest.fixture
def game_url(driver):
    return "file:///Users/njh/.qclaw/workspace/games/breakout/index.html"


class TestBreakoutGame:
    def test_page_loads(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.3)
        assert "打砖块" in driver.title

    def test_canvas_exists(self, driver, game_url):
        driver.get(game_url)
        canvas = driver.find_element(By.TAG_NAME, "canvas")
        assert canvas is not None

    def test_buttons_exist(self, driver, game_url):
        driver.get(game_url)
        assert driver.find_element(By.ID, "startBtn") is not None
        assert driver.find_element(By.ID, "pauseBtn") is not None
        assert driver.find_element(By.ID, "restartBtn") is not None

    def test_start_button_starts_game(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.2)
        driver.find_element(By.ID, "startBtn").click()
        time.sleep(0.3)
        running = driver.execute_script("return running")
        assert running == 1

    def test_reset_button_resets_state(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.2)
        driver.find_element(By.ID, "startBtn").click()
        time.sleep(0.2)
        driver.execute_script("score = 90; x = 280; y = 180;")
        driver.find_element(By.ID, "restartBtn").click()
        time.sleep(0.2)
        state = driver.execute_script("return {running, score, x, y}")
        assert state["running"] == 0
        assert state["score"] == 0
        assert state["x"] == 150
        assert state["y"] == 350

    def test_start_icon_and_feedback_style(self, driver, game_url):
        driver.get(game_url)
        icon = driver.execute_script("return document.getElementById('startBtn').textContent.trim();")
        src = driver.page_source
        assert icon == "▶"
        assert ".btn:active" in src
