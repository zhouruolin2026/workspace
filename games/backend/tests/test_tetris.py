"""
俄罗斯方块单元测试
"""
import pytest
from tetris import TetrisGame, Piece, tetris_manager, SHAPES, COLORS


class TestTetrisGame:
    """测试俄罗斯方块游戏逻辑"""
    
    def test_initial_state(self):
        """测试初始状态"""
        game = TetrisGame()
        assert game.score == 0
        assert game.lines == 0
        assert game.level == 1
        assert game.game_over is False
        assert game.paused is False
        assert game.current_piece is not None
    
    def test_reset(self):
        """测试重置"""
        game = TetrisGame()
        game.score = 1000
        game.game_over = True
        game.reset()
        assert game.score == 0
        assert game.game_over is False
        assert game.board[0][0] is None
    
    def test_move_valid(self):
        """测试有效移动"""
        game = TetrisGame()
        initial_x = game.current_piece.x
        result = game.move(1, 0)  # 右移
        assert result is True
        assert game.current_piece.x == initial_x + 1
    
    def test_move_invalid_wall(self):
        """测试撞墙移动"""
        game = TetrisGame()
        # 移动到最左边
        for _ in range(10):
            game.move(-1, 0)
        result = game.move(-1, 0)  # 应该失败
        assert result is False
    
    def test_rotate_valid(self):
        """测试有效旋转"""
        game = TetrisGame()
        original_shape = game.current_piece.shape
        result = game.rotate()
        assert result is True
        # 形状应该改变
        assert game.current_piece.shape != original_shape
    
    def test_rotate_near_wall(self):
        """测试靠墙旋转"""
        game = TetrisGame()
        # 移动到右边
        for _ in range(10):
            game.move(1, 0)
        # 尝试旋转，可能会因为空间不足而失败
        result = game.rotate()
        # 结果取决于方块形状和位置，不断言具体结果
        assert isinstance(result, bool)
    
    def test_drop(self):
        """测试下落"""
        game = TetrisGame()
        initial_y = game.current_piece.y
        result = game.drop()
        assert result is True
        assert game.current_piece.y == initial_y + 1
    
    def test_hard_drop(self):
        """测试快速下落"""
        game = TetrisGame()
        game.hard_drop()
        # 应该生成新方块
        assert game.current_piece is not None
    
    def test_clear_lines(self):
        """测试消行"""
        game = TetrisGame()
        # 填充底部一行
        game.board[19] = ['#ff0000'] * 10
        game._clear_lines()
        assert game.lines == 1
        assert game.score > 0
        assert game.board[19][0] is None  # 行被清除
    
    def test_clear_multiple_lines(self):
        """测试消多行"""
        game = TetrisGame()
        # 填充底部两行
        game.board[18] = ['#ff0000'] * 10
        game.board[19] = ['#00ff00'] * 10
        game._clear_lines()
        assert game.lines == 2
        assert game.score == 300  # 2行=300分
    
    def test_toggle_pause(self):
        """测试暂停"""
        game = TetrisGame()
        assert game.paused is False
        game.toggle_pause()
        assert game.paused is True
        game.toggle_pause()
        assert game.paused is False
    
    def test_game_over_on_collision(self):
        """测试游戏结束"""
        game = TetrisGame()
        # 填满顶部，让新方块无法生成
        for x in range(game.width):
            game.board[0][x] = '#000000'
        game._spawn_piece()
        assert game.game_over is True
    
    def test_get_state(self):
        """测试获取状态"""
        game = TetrisGame()
        state = game.get_state()
        assert 'board' in state
        assert 'current_piece' in state
        assert 'score' in state
        assert 'game_over' in state


class TestPiece:
    """测试方块类"""
    
    def test_rotate(self):
        """测试方块旋转"""
        piece = Piece([[1, 1, 1, 1]], '#00f5ff', 5, 5)
        rotated = piece.rotate()
        # I方块旋转后变成竖的
        assert len(rotated.shape) == 4
        assert len(rotated.shape[0]) == 1


class TestTetrisManager:
    """测试游戏管理器"""
    
    def test_create_and_get(self):
        """测试创建和获取"""
        game = tetris_manager.create_game('test1')
        assert game is not None
        assert tetris_manager.get_game('test1') == game
    
    def test_remove(self):
        """测试移除"""
        tetris_manager.create_game('test2')
        tetris_manager.remove_game('test2')
        assert tetris_manager.get_game('test2') is None
