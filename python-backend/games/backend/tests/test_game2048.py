"""
2048 单元测试
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game2048 import Game2048, game_2048_manager


class TestGame2048:
    """测试 2048 游戏逻辑"""
    
    def test_initial_state(self):
        """测试初始状态"""
        game = Game2048()
        assert game.size == 4
        assert game.score == 0
        assert game.game_over is False
        assert game.won is False
        # 初始应该有两个数字
        non_zero_count = sum(1 for row in game.board for cell in row if cell != 0)
        assert non_zero_count == 2
    
    def test_custom_size(self):
        """测试自定义棋盘大小"""
        game = Game2048(size=5)
        assert game.size == 5
        assert len(game.board) == 5
        assert len(game.board[0]) == 5
    
    def test_reset(self):
        """测试重置游戏"""
        game = Game2048()
        game.score = 100
        game.game_over = True
        game.won = True
        game.reset()
        assert game.score == 0
        assert game.game_over is False
        assert game.won is False
        non_zero_count = sum(1 for row in game.board for cell in row if cell != 0)
        assert non_zero_count == 2
    
    def test_slide_row_simple(self):
        """测试简单行滑动"""
        game = Game2048()
        game.board = [[0] * 4 for _ in range(4)]
        result = game._slide_row([2, 0, 0, 0])
        assert result == [2, 0, 0, 0]
    
    def test_slide_row_merge(self):
        """测试行合并"""
        game = Game2048()
        game.board = [[0] * 4 for _ in range(4)]
        game.score = 0
        result = game._slide_row([2, 2, 0, 0])
        assert result == [4, 0, 0, 0]
        assert game.score == 4
    
    def test_slide_row_multiple_merge(self):
        """测试多组合并"""
        game = Game2048()
        game.board = [[0] * 4 for _ in range(4)]
        game.score = 0
        result = game._slide_row([2, 2, 4, 4])
        assert result == [4, 8, 0, 0]
        assert game.score == 12
    
    def test_slide_row_no_merge_different(self):
        """测试不同数字不合并"""
        game = Game2048()
        game.board = [[0] * 4 for _ in range(4)]
        result = game._slide_row([2, 4, 0, 0])
        assert result == [2, 4, 0, 0]
    
    def test_slide_row_chain_merge_blocked(self):
        """测试三连相同数字只合并前两个"""
        game = Game2048()
        game.board = [[0] * 4 for _ in range(4)]
        game.score = 0
        result = game._slide_row([2, 2, 2, 0])
        # 应该合并前两个2变成4，留下最后一个2
        assert result == [4, 2, 0, 0]
        assert game.score == 4
    
    def test_slide_row_four_same(self):
        """测试四个相同数字合并成两个"""
        game = Game2048()
        game.board = [[0] * 4 for _ in range(4)]
        game.score = 0
        result = game._slide_row([2, 2, 2, 2])
        assert result == [4, 4, 0, 0]
        assert game.score == 8
    
    def test_move_left(self):
        """测试左移"""
        game = Game2048()
        game.board = [
            [2, 0, 2, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        changed = game.move('LEFT')
        assert changed is True
        assert game.board[0][0] == 4
        assert game.board[0][1] == 0
    
    def test_move_right(self):
        """测试右移"""
        game = Game2048()
        game.board = [
            [2, 0, 2, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        changed = game.move('RIGHT')
        assert changed is True
        assert game.board[0][3] == 4
        assert game.board[0][2] == 0
    
    def test_move_up(self):
        """测试上移"""
        game = Game2048()
        game.board = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        changed = game.move('UP')
        assert changed is True
        assert game.board[0][0] == 4
        assert game.board[1][0] == 0
    
    def test_move_down(self):
        """测试下移"""
        game = Game2048()
        game.board = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        changed = game.move('DOWN')
        assert changed is True
        # 下移后两个2合并成4，在最底部
        assert game.board[3][0] == 4
        # 由于移动后会生成新数字，检查其他位置
    
    def test_move_no_change(self):
        """测试无效移动（无变化）"""
        game = Game2048()
        game.board = [
            [4, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        changed = game.move('LEFT')
        assert changed is False
    
    def test_move_spawns_new_tile(self):
        """测试移动后生成新数字"""
        game = Game2048()
        game.board = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        initial_count = sum(1 for row in game.board for cell in row if cell != 0)
        game.move('LEFT')  # 不会变化，因为已经在最左
        # 手动设置一个可以移动的情况
        game.board = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        game.move('RIGHT')
        # 移动后应该还是只有一个2（在最右边），加上新生成的一个
        non_zero_count = sum(1 for row in game.board for cell in row if cell != 0)
        assert non_zero_count >= 2  # 至少原来的那个加上新生成的
    
    def test_win_condition(self):
        """测试获胜条件"""
        game = Game2048()
        game.board = [
            [1024, 1024, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        game.move('LEFT')
        assert game.won is True
    
    def test_game_over_no_moves(self):
        """测试无法移动时游戏结束"""
        game = Game2048()
        # 填满棋盘且无法合并
        game.board = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2]
        ]
        game._check_game_over()
        assert game.game_over is True
    
    def test_game_over_can_merge(self):
        """测试可以合并时游戏不结束"""
        game = Game2048()
        game.board = [
            [2, 2, 4, 8],
            [4, 8, 16, 32],
            [8, 16, 32, 64],
            [16, 32, 64, 128]
        ]
        game._check_game_over()
        assert game.game_over is False
    
    def test_game_over_has_empty(self):
        """测试有空格时游戏不结束"""
        game = Game2048()
        game.board = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 0, 4],
            [4, 2, 4, 2]
        ]
        game._check_game_over()
        assert game.game_over is False
    
    def test_get_state(self):
        """测试获取游戏状态"""
        game = Game2048()
        state = game.get_state()
        assert 'board' in state
        assert 'score' in state
        assert 'game_over' in state
        assert 'won' in state
        assert 'size' in state
    
    def test_get_empty_cells(self):
        """测试获取空单元格"""
        game = Game2048()
        game.board = [
            [2, 0, 2, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        empty = game.get_empty_cells()
        assert len(empty) == 14  # 16 - 2
        assert (0, 1) in empty
        assert (0, 0) not in empty
    
    def test_invalid_direction(self):
        """测试无效方向"""
        game = Game2048()
        result = game.move('INVALID')
        assert result is False
    
    def test_move_when_game_over(self):
        """测试游戏结束后不能移动"""
        game = Game2048()
        game.game_over = True
        result = game.move('LEFT')
        assert result is False


class TestGame2048Manager:
    """测试游戏管理器"""
    
    def test_create_game(self):
        """测试创建游戏"""
        game = game_2048_manager.create_game('test1')
        assert game is not None
        assert game_2048_manager.get_game('test1') == game
    
    def test_create_game_custom_size(self):
        """测试创建自定义大小游戏"""
        game = game_2048_manager.create_game('test2', size=5)
        assert game.size == 5
    
    def test_get_nonexistent_game(self):
        """测试获取不存在的游戏"""
        assert game_2048_manager.get_game('nonexistent') is None
    
    def test_remove_game(self):
        """测试移除游戏"""
        game_2048_manager.create_game('test3')
        game_2048_manager.remove_game('test3')
        assert game_2048_manager.get_game('test3') is None
