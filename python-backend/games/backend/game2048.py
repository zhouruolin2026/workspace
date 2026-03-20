"""
2048 游戏逻辑 - 后端实现
"""
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from copy import deepcopy


@dataclass
class Game2048:
    size: int = 4
    
    def __post_init__(self):
        self.reset()
    
    def reset(self):
        """重置游戏状态"""
        self.board: List[List[int]] = [[0] * self.size for _ in range(self.size)]
        self.score = 0
        self.game_over = False
        self.won = False
        self._spawn_tile()
        self._spawn_tile()
    
    def _spawn_tile(self):
        """在随机空位置生成新数字（90%概率是2，10%概率是4）"""
        empty_cells = []
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    empty_cells.append((i, j))
        
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 4 if random.random() < 0.1 else 2
    
    def _slide_row(self, row: List[int]) -> List[int]:
        """将一行向左滑动并合并"""
        # 移除所有0
        non_zero = [x for x in row if x != 0]
        
        # 合并相同的数字
        merged = []
        i = 0
        while i < len(non_zero):
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged_value = non_zero[i] * 2
                merged.append(merged_value)
                self.score += merged_value
                if merged_value == 2048:
                    self.won = True
                i += 2
            else:
                merged.append(non_zero[i])
                i += 1
        
        # 补0
        merged += [0] * (self.size - len(merged))
        return merged
    
    def _move_left(self) -> bool:
        """向左移动，返回是否有变化"""
        changed = False
        for i in range(self.size):
            old_row = self.board[i][:]
            self.board[i] = self._slide_row(self.board[i])
            if old_row != self.board[i]:
                changed = True
        return changed
    
    def _rotate_clockwise(self):
        """顺时针旋转棋盘90度"""
        self.board = [list(row) for row in zip(*self.board[::-1])]
    
    def _rotate_counter_clockwise(self):
        """逆时针旋转棋盘90度"""
        self.board = [list(row) for row in zip(*self.board)][::-1]
    
    def move(self, direction: str) -> bool:
        """
        执行移动操作
        direction: 'UP', 'DOWN', 'LEFT', 'RIGHT'
        返回是否有变化
        """
        if self.game_over:
            return False
        
        direction = direction.upper()
        
        # 保存旧状态用于比较
        old_board = deepcopy(self.board)
        
        if direction == 'LEFT':
            changed = self._move_left()
        elif direction == 'RIGHT':
            # 右移 = 翻转 -> 左移 -> 翻转回来
            self.board = [row[::-1] for row in self.board]
            changed = self._move_left()
            self.board = [row[::-1] for row in self.board]
        elif direction == 'UP':
            # 上移 = 逆时针旋转 -> 左移 -> 顺时针旋转回来
            self._rotate_counter_clockwise()
            changed = self._move_left()
            self._rotate_clockwise()
        elif direction == 'DOWN':
            # 下移 = 顺时针旋转 -> 左移 -> 逆时针旋转回来
            self._rotate_clockwise()
            changed = self._move_left()
            self._rotate_counter_clockwise()
        else:
            return False
        
        if changed:
            self._spawn_tile()
            self._check_game_over()
        
        return changed
    
    def _check_game_over(self):
        """检查游戏是否结束"""
        # 检查是否还有空格
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return
        
        # 检查是否还能合并
        for i in range(self.size):
            for j in range(self.size):
                current = self.board[i][j]
                # 检查右边
                if j + 1 < self.size and self.board[i][j + 1] == current:
                    return
                # 检查下边
                if i + 1 < self.size and self.board[i + 1][j] == current:
                    return
        
        self.game_over = True
    
    def get_state(self) -> Dict:
        """获取游戏状态"""
        return {
            'board': self.board,
            'score': self.score,
            'game_over': self.game_over,
            'won': self.won,
            'size': self.size
        }
    
    def get_empty_cells(self) -> List[tuple]:
        """获取所有空单元格位置"""
        empty = []
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    empty.append((i, j))
        return empty


# 游戏实例管理器
class Game2048Manager:
    def __init__(self):
        self.games: Dict[str, Game2048] = {}
    
    def create_game(self, game_id: str, size: int = 4) -> Game2048:
        """创建新游戏"""
        game = Game2048(size)
        self.games[game_id] = game
        return game
    
    def get_game(self, game_id: str) -> Optional[Game2048]:
        """获取游戏实例"""
        return self.games.get(game_id)
    
    def remove_game(self, game_id: str):
        """移除游戏"""
        if game_id in self.games:
            del self.games[game_id]


# 全局游戏管理器
game_2048_manager = Game2048Manager()
