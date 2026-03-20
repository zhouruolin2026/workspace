"""
贪吃蛇游戏逻辑 - 后端实现
"""
import random
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


@dataclass
class SnakeGame:
    width: int = 20
    height: int = 20
    
    def __post_init__(self):
        self.reset()
    
    def reset(self):
        """重置游戏状态"""
        # 蛇身，从头部开始
        self.snake: List[Tuple[int, int]] = [
            (self.width // 2, self.height // 2),
            (self.width // 2 - 1, self.height // 2),
            (self.width // 2 - 2, self.height // 2)
        ]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.game_over = False
        self._place_food()
    
    def _place_food(self):
        """放置食物"""
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break
    
    def change_direction(self, direction: str) -> bool:
        """改变方向，不能反向"""
        if self.game_over:
            return False
            
        direction_map = {
            'UP': Direction.UP,
            'DOWN': Direction.DOWN,
            'LEFT': Direction.LEFT,
            'RIGHT': Direction.RIGHT
        }
        
        if direction not in direction_map:
            return False
            
        new_dir = direction_map[direction]
        
        # 不能反向
        if (new_dir.value[0] != -self.next_direction.value[0] or 
            new_dir.value[1] != -self.next_direction.value[1]):
            self.next_direction = new_dir
            return True
        return False
    
    def step(self) -> bool:
        """游戏前进一步，返回是否成功"""
        if self.game_over:
            return False
        
        self.direction = self.next_direction
        dx, dy = self.direction.value
        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)
        
        # 撞墙检测
        if (new_head[0] < 0 or new_head[0] >= self.width or
            new_head[1] < 0 or new_head[1] >= self.height):
            self.game_over = True
            return False
        
        # 撞自己检测
        if new_head in self.snake:
            self.game_over = True
            return False
        
        # 移动蛇
        self.snake.insert(0, new_head)
        
        # 吃食物
        if new_head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()
        
        return True
    
    def get_state(self) -> Dict:
        """获取游戏状态"""
        return {
            'snake': self.snake,
            'food': self.food,
            'score': self.score,
            'game_over': self.game_over,
            'width': self.width,
            'height': self.height
        }


# 游戏实例管理器
class SnakeGameManager:
    def __init__(self):
        self.games: Dict[str, SnakeGame] = {}
    
    def create_game(self, game_id: str) -> SnakeGame:
        """创建新游戏"""
        game = SnakeGame()
        self.games[game_id] = game
        return game
    
    def get_game(self, game_id: str) -> Optional[SnakeGame]:
        """获取游戏实例"""
        return self.games.get(game_id)
    
    def remove_game(self, game_id: str):
        """移除游戏"""
        if game_id in self.games:
            del self.games[game_id]


# 全局游戏管理器
game_manager = SnakeGameManager()
