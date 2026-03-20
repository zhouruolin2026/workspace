"""
俄罗斯方块游戏逻辑 - 后端实现
"""
import random
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from copy import deepcopy


# 方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],           # I
    [[1, 1], [1, 1]],         # O
    [[0, 1, 0], [1, 1, 1]],   # T
    [[0, 1, 1], [1, 1, 0]],   # S
    [[1, 1, 0], [0, 1, 1]],   # Z
    [[1, 0, 0], [1, 1, 1]],   # J
    [[0, 0, 1], [1, 1, 1]]    # L
]

COLORS = [
    '#00f5ff', '#ffeb3b', '#9c27b0', '#4caf50',
    '#f44336', '#2196f3', '#ff9800'
]


@dataclass
class Piece:
    shape: List[List[int]]
    color: str
    x: int
    y: int
    
    def rotate(self) -> 'Piece':
        """返回旋转后的新方块"""
        rotated = [list(row) for row in zip(*self.shape[::-1])]
        return Piece(rotated, self.color, self.x, self.y)


class TetrisGame:
    def __init__(self, width: int = 10, height: int = 20):
        self.width = width
        self.height = height
        self.reset()
    
    def reset(self):
        """重置游戏"""
        self.board: List[List[str]] = [[None for _ in range(self.width)] 
                                        for _ in range(self.height)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.next_piece = self._create_piece()
        self._spawn_piece()
    
    def _create_piece(self) -> Piece:
        """创建新方块"""
        idx = random.randint(0, len(SHAPES) - 1)
        shape = [row[:] for row in SHAPES[idx]]
        x = self.width // 2 - len(shape[0]) // 2
        return Piece(shape, COLORS[idx], x, 0)
    
    def _spawn_piece(self) -> bool:
        """生成新方块"""
        self.current_piece = self.next_piece
        self.next_piece = self._create_piece()
        
        if self._check_collision(self.current_piece):
            self.game_over = True
            return False
        return True
    
    def _check_collision(self, piece: Piece, dx: int = 0, dy: int = 0) -> bool:
        """检测碰撞"""
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    nx = piece.x + x + dx
                    ny = piece.y + y + dy
                    if nx < 0 or nx >= self.width or ny >= self.height:
                        return True
                    if ny >= 0 and self.board[ny][nx] is not None:
                        return True
        return False
    
    def _merge_piece(self):
        """固定当前方块到棋盘"""
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    ny = self.current_piece.y + y
                    nx = self.current_piece.x + x
                    if 0 <= ny < self.height:
                        self.board[ny][nx] = self.current_piece.color
    
    def _clear_lines(self) -> int:
        """清除满行，返回清除行数"""
        cleared = 0
        y = self.height - 1
        while y >= 0:
            if all(cell is not None for cell in self.board[y]):
                del self.board[y]
                self.board.insert(0, [None for _ in range(self.width)])
                cleared += 1
            else:
                y -= 1
        
        if cleared > 0:
            self.lines += cleared
            self.score += [0, 100, 300, 600, 1000][min(cleared, 4)] * self.level
            self.level = self.lines // 10 + 1
        
        return cleared
    
    def move(self, dx: int, dy: int) -> bool:
        """移动方块"""
        if self.game_over or self.paused:
            return False
        
        if not self._check_collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False
    
    def rotate(self) -> bool:
        """旋转方块"""
        if self.game_over or self.paused:
            return False
        
        rotated = self.current_piece.rotate()
        if not self._check_collision(rotated):
            self.current_piece = rotated
            return True
        return False
    
    def drop(self) -> bool:
        """下落一步"""
        if self.game_over or self.paused:
            return False
        
        if not self.move(0, 1):
            self._merge_piece()
            self._clear_lines()
            if not self._spawn_piece():
                return False
        return True
    
    def hard_drop(self):
        """快速下落"""
        if self.game_over or self.paused:
            return
        
        while self.move(0, 1):
            pass
        self._merge_piece()
        self._clear_lines()
        self._spawn_piece()
    
    def toggle_pause(self):
        """暂停/继续"""
        if not self.game_over:
            self.paused = not self.paused
    
    def get_state(self) -> Dict:
        """获取游戏状态"""
        return {
            'board': self.board,
            'current_piece': {
                'shape': self.current_piece.shape,
                'color': self.current_piece.color,
                'x': self.current_piece.x,
                'y': self.current_piece.y
            } if self.current_piece else None,
            'next_piece': {
                'shape': self.next_piece.shape,
                'color': self.next_piece.color
            } if self.next_piece else None,
            'score': self.score,
            'lines': self.lines,
            'level': self.level,
            'game_over': self.game_over,
            'paused': self.paused,
            'width': self.width,
            'height': self.height
        }


# 游戏管理器
class TetrisGameManager:
    def __init__(self):
        self.games: Dict[str, TetrisGame] = {}
    
    def create_game(self, game_id: str) -> TetrisGame:
        game = TetrisGame()
        self.games[game_id] = game
        return game
    
    def get_game(self, game_id: str) -> Optional[TetrisGame]:
        return self.games.get(game_id)
    
    def remove_game(self, game_id: str):
        if game_id in self.games:
            del self.games[game_id]


tetris_manager = TetrisGameManager()
