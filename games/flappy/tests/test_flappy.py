"""
跳跳鸟游戏 Selenium 自动化测试
"""
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def driver():
    """创建浏览器驱动"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=400,600')
    
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()


@pytest.fixture
def game_url(driver):
    """游戏页面 URL"""
    return "file:///Users/njh/.qclaw/workspace/games/flappy/index.html"


class TestFlappyBirdGame:
    """测试跳跳鸟游戏"""
    
    def test_page_loads(self, driver, game_url):
        """测试页面加载"""
        driver.get(game_url)
        time.sleep(0.5)
        assert "跳跳鸟" in driver.title
    
    def test_canvas_exists(self, driver, game_url):
        """测试画布存在"""
        driver.get(game_url)
        time.sleep(0.5)
        canvas = driver.find_element(By.TAG_NAME, "canvas")
        assert canvas is not None
    
    def test_button_exists(self, driver, game_url):
        """测试按钮存在"""
        driver.get(game_url)
        time.sleep(1)
        buttons = driver.find_elements(By.TAG_NAME, "button")
        assert len(buttons) > 0
    
    def test_button_has_id(self, driver, game_url):
        """测试按钮有正确的ID"""
        driver.get(game_url)
        time.sleep(1)
        assert driver.find_element(By.ID, "startBtn") is not None
        assert driver.find_element(By.ID, "pauseBtn") is not None
        assert driver.find_element(By.ID, "restartBtn") is not None
    
    def test_initial_button_text(self, driver, game_url):
        """测试初始按钮可见"""
        driver.get(game_url)
        time.sleep(1)
        button = driver.find_element(By.ID, "startBtn")
        assert button.is_displayed()

    def test_click_start_enters_running_state(self, driver, game_url):
        """测试点击开始后进入运行状态"""
        driver.get(game_url)
        time.sleep(0.3)
        button = driver.find_element(By.ID, "startBtn")
        button.click()
        time.sleep(0.3)

        running = driver.execute_script("return running")
        assert running == 1

    def test_click_restart_resets_game_state(self, driver, game_url):
        """测试再次点击会重置游戏状态"""
        driver.get(game_url)
        time.sleep(0.3)
        driver.find_element(By.ID, "startBtn").click()
        time.sleep(0.3)
        driver.find_element(By.ID, "restartBtn").click()
        time.sleep(0.3)

        state = driver.execute_script(
            "return {running, paused, birdY, birdV, score, pipesLen: pipes.length};"
        )
        assert state["running"] == 0
        assert state["paused"] == 0
        assert state["birdY"] == 225
        assert state["birdV"] == 0
        assert state["score"] == 0
        assert state["pipesLen"] == 0

    def test_update_generates_pipe(self, driver, game_url):
        """测试 update 会生成管道"""
        driver.get(game_url)
        time.sleep(0.3)

        pipe_count = driver.execute_script(
            """
            window.requestAnimationFrame = function(){};
            running = 1;
            pipes = [];
            birdY = 225;
            birdV = 0;
            update();
            return pipes.length;
            """
        )
        assert pipe_count >= 1

    def test_touch_flap_sets_negative_velocity(self, driver, game_url):
        """测试触摸时小鸟上跳（速度变负）"""
        driver.get(game_url)
        time.sleep(0.3)

        bird_v = driver.execute_script(
            """
            running = 1;
            birdV = 0;
            c.ontouchstart({preventDefault: function(){}});
            return birdV;
            """
        )
        assert bird_v == -8

    def test_space_key_starts_game(self, driver, game_url):
        """测试空格键可启动游戏"""
        driver.get(game_url)
        time.sleep(0.3)

        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.SPACE)
        time.sleep(0.3)

        running = driver.execute_script("return running")
        assert running == 1

    def test_out_of_bounds_ends_game(self, driver, game_url):
        """测试越界会结束游戏"""
        driver.get(game_url)
        time.sleep(0.3)

        state = driver.execute_script(
            """
            window.requestAnimationFrame = function(){};
            running = 1;
            birdY = 500;
            birdV = 0;
            update();
            return {running, btnText: document.getElementById('startBtn').textContent};
            """
        )
        assert state["running"] == 0
        assert state["btnText"] is not None

    def test_restart_after_game_over_starts_again(self, driver, game_url):
        """测试结束后点击重新开始可重新进入运行状态"""
        driver.get(game_url)
        time.sleep(0.3)

        driver.execute_script(
            """
            window.requestAnimationFrame = function(){};
            running = 1;
            birdY = 500;
            birdV = 0;
            update();
            """
        )
        button = driver.find_element(By.ID, "startBtn")
        button.click()
        time.sleep(0.2)
        state = driver.execute_script("return {running, birdY, score, pipesLen: pipes.length}")
        assert state["running"] == 1
        assert 225 <= state["birdY"] <= 226
        assert state["score"] == 0

    def test_start_icon_and_feedback_style(self, driver, game_url):
        driver.get(game_url)
        icon = driver.execute_script("return document.getElementById('startBtn').textContent.trim();")
        src = driver.page_source
        assert icon == "▶"
        assert ".btn:active" in src
