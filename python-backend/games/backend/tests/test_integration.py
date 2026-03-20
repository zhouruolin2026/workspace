"""
系统集成测试 - API 测试
"""
import pytest
import json

# 添加 backend 目录到路径
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from server import app


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestSnakeAPI:
    """测试贪吃蛇 API"""
    
    def test_create_game(self, client):
        """测试创建游戏"""
        response = client.post('/api/snake/new')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'game_id' in data
        assert 'state' in data
        assert data['state']['score'] == 0
    
    def test_get_state(self, client):
        """测试获取状态"""
        # 先创建游戏
        response = client.post('/api/snake/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        
        # 获取状态
        response = client.get(f'/api/snake/{game_id}/state')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'snake' in data
    
    def test_get_state_not_found(self, client):
        """测试获取不存在的游戏"""
        response = client.get('/api/snake/invalid/state')
        assert response.status_code == 404
    
    def test_move(self, client):
        """测试移动"""
        # 创建游戏
        response = client.post('/api/snake/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        
        # 改变方向
        response = client.post(f'/api/snake/{game_id}/move',
                              data=json.dumps({'direction': 'UP'}),
                              content_type='application/json')
        assert response.status_code == 200
    
    def test_step(self, client):
        """测试前进一步"""
        # 创建游戏
        response = client.post('/api/snake/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        initial_x = data['state']['snake'][0][0]
        
        # 前进一步
        response = client.post(f'/api/snake/{game_id}/step')
        assert response.status_code == 200
        data = json.loads(response.data)
        # 蛇应该向右移动（默认方向）
        assert data['snake'][0][0] == initial_x + 1
    
    def test_reset(self, client):
        """测试重置"""
        # 创建游戏并移动几步
        response = client.post('/api/snake/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        
        client.post(f'/api/snake/{game_id}/step')
        
        # 重置
        response = client.post(f'/api/snake/{game_id}/reset')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['score'] == 0


class TestTetrisAPI:
    """测试俄罗斯方块 API"""
    
    def test_create_game(self, client):
        """测试创建游戏"""
        response = client.post('/api/tetris/new')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'game_id' in data
        assert data['state']['score'] == 0
    
    def test_move(self, client):
        """测试移动"""
        response = client.post('/api/tetris/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        initial_x = data['state']['current_piece']['x']
        
        # 右移
        response = client.post(f'/api/tetris/{game_id}/move',
                              data=json.dumps({'dx': 1, 'dy': 0}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['current_piece']['x'] == initial_x + 1
    
    def test_rotate(self, client):
        """测试旋转"""
        response = client.post('/api/tetris/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        
        response = client.post(f'/api/tetris/{game_id}/rotate')
        assert response.status_code == 200
    
    def test_drop(self, client):
        """测试下落"""
        response = client.post('/api/tetris/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        initial_y = data['state']['current_piece']['y']
        
        response = client.post(f'/api/tetris/{game_id}/drop')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['current_piece']['y'] == initial_y + 1
    
    def test_hard_drop(self, client):
        """测试快速下落"""
        response = client.post('/api/tetris/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        
        response = client.post(f'/api/tetris/{game_id}/hard_drop')
        assert response.status_code == 200
    
    def test_pause(self, client):
        """测试暂停"""
        response = client.post('/api/tetris/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        
        response = client.post(f'/api/tetris/{game_id}/pause')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['paused'] is True
    
    def test_reset(self, client):
        """测试重置"""
        response = client.post('/api/tetris/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        
        # 移动几步
        client.post(f'/api/tetris/{game_id}/drop')
        
        # 重置
        response = client.post(f'/api/tetris/{game_id}/reset')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['score'] == 0


class TestStaticFiles:
    """测试静态文件"""
    
    def test_index(self, client):
        """测试首页"""
        response = client.get('/')
        # 如果没有 index.html 会 404，这是正常的
        assert response.status_code in [200, 404]
