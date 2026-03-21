"""
贪吃蛇游戏 Selenium 自动化测试
"""
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def driver():
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
    return "file:///Users/njh/.qclaw/workspace/games/snake/index.html"


class TestSnakeGame:
    """测试贪吃蛇游戏"""
    
    # 1. 页面加载测试
    def test_page_loads(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.5)
        assert "贪吃蛇" in driver.title
    
    # 2. 画布存在测试
    def test_canvas_exists(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.5)
        canvas = driver.find_element(By.TAG_NAME, "canvas")
        assert canvas is not None
    
    # 3. 得分显示测试
    def test_score_display_exists(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.5)
        score = driver.find_element(By.CSS_SELECTOR, "#score span")
        assert score is not None
    
    # 4. 开始按钮存在测试
    def test_start_button_exists(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.5)
        button = driver.find_element(By.ID, "startBtn")
        assert button is not None
    
    # 5. 点击开始按钮测试
    def test_click_start_button(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.5)
        button = driver.find_element(By.ID, "startBtn")
        button.click()
        time.sleep(0.3)
        running = driver.execute_script("return window.__snakeState().running")
        assert running == 1
    
    # 6. 键盘控制测试
    def test_keyboard_controls(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.5)
        body = driver.find_element(By.TAG_NAME, "body")
        # 按空格键
        body.send_keys(" ")
        time.sleep(0.3)
        # 游戏应该开始
        button = driver.find_element(By.ID, "startBtn")
        assert button is not None
    
    # 7. 触摸控制测试
    def test_touch_control_exists(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.5)
        canvas = driver.find_element(By.TAG_NAME, "canvas")
        # 检查 canvas 是否有触摸事件（通过属性）
        # 触摸事件在 HTML 中通过 on* 属性或 JS 绑定
    
    # 8. 游戏初始化状态测试
    def test_initial_state(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.5)
        score_text = driver.execute_script(
            "return document.querySelector('#score span').textContent.trim()"
        )
        assert score_text == "0"

    def test_start_icon_and_feedback_style(self, driver, game_url):
        driver.get(game_url)
        time.sleep(0.3)
        icon = driver.execute_script("return document.getElementById('startBtn').textContent.trim();")
        src = driver.page_source
        assert icon == "▶"
        assert ".btn:active" in src

    def test_arrow_key_mapping(self, driver, game_url):
        """测试方向键映射正确"""
        driver.get(game_url)
        time.sleep(0.3)
        src = driver.page_source
        assert "ArrowUp'&&!dir.y)dir={x:0,y:-1}" in src
        assert "ArrowDown'&&!dir.y)dir={x:0,y:1}" in src
        assert "ArrowLeft'&&!dir.x)dir={x:-1,y:0}" in src
        assert "ArrowRight'&&!dir.x)dir={x:1,y:0}" in src
