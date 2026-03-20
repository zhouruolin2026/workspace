"""
贪吃蛇单元测试
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from snake import SnakeGame, Direction, game_manager


class TestSnakeGame:
    """测试贪吃蛇游戏逻辑"""
    
    def test_initial_state(self):
        """测试初始状态"""
        game = SnakeGame(20, 20)
        assert len(game.snake) == 3
        assert game.score == 0
        assert game.game_over is False
        assert game.direction == Direction.RIGHT
    
    def test_change_direction_valid(self):
        """测试有效方向改变"""
        game = SnakeGame()
        assert game.change_direction('UP') is True
        assert game.next_direction == Direction.UP
    
    def test_change_direction_invalid_reverse(self):
        """测试不能反向"""
        game = SnakeGame()
        # 初始向右，不能立即向左
        assert game.change_direction('LEFT') is False
        assert game.next_direction == Direction.RIGHT
    
    def test_change_direction_after_turn(self):
        """测试转向后可以反向"""
        game = SnakeGame()
        game.change_direction('UP')
        game.step()
        # 现在向上，可以向右（原方向的反方向）
        assert game.change_direction('RIGHT') is True
    
    def test_step_moves_snake(self):
        """测试蛇移动"""
        game = SnakeGame()
        initial_head = game.snake[0]
        game.step()
        new_head = game.snake[0]
        assert new_head[0] == initial_head[0] + 1  # 向右移动
        assert new_head[1] == initial_head[1]
    
    def test_eat_food(self):
        """测试吃食物"""
        game = SnakeGame()
        # 强制把食物放在蛇头前方
        game.food = (game.snake[0][0] + 1, game.snake[0][1])
        initial_length = len(game.snake)
        game.step()
        assert len(game.snake) == initial_length + 1
        assert game.score == 1
    
    def test_hit_wall(self):
        """测试撞墙"""
        game = SnakeGame(5, 5)
        game.snake = [(4, 2), (3, 2), (2, 2)]  # 靠近右墙
        game.direction = Direction.RIGHT
        game.next_direction = Direction.RIGHT
        game.step()
        assert game.game_over is True
    
    def test_hit_self(self):
        """测试撞自己"""
        game = SnakeGame()
        # 制造撞自己的情况 - 蛇头向上移动会撞到自己的身体
        game.snake = [(5, 5), (5, 6), (6, 6), (6, 5), (6, 4)]
        game.direction = Direction.DOWN
        game.next_direction = Direction.DOWN
        game.step()  # 会撞到 (5,6)
        assert game.game_over is True
    
    def test_reset(self):
        """测试重置游戏"""
        game = SnakeGame()
        game.score = 100
        game.game_over = True
        game.reset()
        assert game.score == 0
        assert game.game_over is False
        assert len(game.snake) == 3
    
    def test_get_state(self):
        """测试获取状态"""
        game = SnakeGame()
        state = game.get_state()
        assert 'snake' in state
        assert 'food' in state
        assert 'score' in state
        assert 'game_over' in state


class TestGameManager:
    """测试游戏管理器"""
    
    def test_create_game(self):
        """测试创建游戏"""
        game = game_manager.create_game('test1')
        assert game is not None
        assert game_manager.get_game('test1') == game
    
    def test_get_nonexistent_game(self):
        """测试获取不存在的游戏"""
        assert game_manager.get_game('nonexistent') is None
    
    def test_remove_game(self):
        """测试移除游戏"""
        game_manager.create_game('test2')
        game_manager.remove_game('test2')
        assert game_manager.get_game('test2') is None
