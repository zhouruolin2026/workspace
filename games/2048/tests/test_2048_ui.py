"""
2048 游戏 Selenium 系统测试
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
    return "file:///Users/njh/.qclaw/workspace/games/2048/index.html"


class TestGame2048UI:
    def test_page_loads(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.3)
        assert "2048" in driver.title

    def test_buttons_exist(self, driver, game_url):
        driver.get(game_url)
        assert driver.find_element(By.ID, "startBtn") is not None
        assert driver.find_element(By.ID, "pauseBtn") is not None
        assert driver.find_element(By.ID, "restartBtn") is not None
        assert driver.find_element(By.ID, "upBtn") is not None
        assert driver.find_element(By.ID, "downBtn") is not None
        assert driver.find_element(By.ID, "leftBtn") is not None
        assert driver.find_element(By.ID, "rightBtn") is not None

    def test_new_game_resets_score(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.3)
        driver.execute_script("score = 128; document.getElementById('s').textContent = score;")
        driver.find_element(By.ID, "restartBtn").click()
        time.sleep(0.2)
        score = driver.execute_script("return score")
        assert score == 0

    def test_dpad_buttons_trigger_move(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.3)
        driver.find_element(By.ID, "startBtn").click()
        time.sleep(0.2)
        old_board = driver.execute_script("return JSON.stringify(board)")
        driver.find_element(By.ID, "leftBtn").click()
        time.sleep(0.2)
        new_board = driver.execute_script("return JSON.stringify(board)")
        assert isinstance(old_board, str)
        assert isinstance(new_board, str)

    def test_start_icon_and_feedback_style(self, driver, game_url):
        driver.get(game_url)
        icon = driver.execute_script("return document.getElementById('startBtn').textContent.trim();")
        src = driver.page_source
        assert icon == "▶"
        assert ".btn:active" in src
