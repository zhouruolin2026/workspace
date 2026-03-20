"""
2048 系统集成测试 - API 测试
"""
import pytest
import json
import sys
import os

# 添加 backend 目录到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from server import app


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class Test2048API:
    """测试 2048 API"""
    
    def test_create_game(self, client):
        """测试创建游戏"""
        response = client.post('/api/2048/new')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'game_id' in data
        assert 'state' in data
        assert data['state']['score'] == 0
        assert data['state']['size'] == 4
    
    def test_create_game_custom_size(self, client):
        """测试创建自定义大小游戏"""
        response = client.post('/api/2048/new',
                              data=json.dumps({'size': 5}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['state']['size'] == 5
    
    def test_get_state(self, client):
        """测试获取状态"""
        # 先创建游戏
        response = client.post('/api/2048/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        
        # 获取状态
        response = client.get(f'/api/2048/{game_id}/state')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'board' in data
        assert 'score' in data
    
    def test_get_state_not_found(self, client):
        """测试获取不存在的游戏"""
        response = client.get('/api/2048/invalid/state')
        assert response.status_code == 404
    
    def test_move(self, client):
        """测试移动"""
        # 创建游戏
        response = client.post('/api/2048/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        
        # 移动
        response = client.post(f'/api/2048/{game_id}/move',
                              data=json.dumps({'direction': 'LEFT'}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'changed' in data
        assert 'board' in data
    
    def test_move_invalid_direction(self, client):
        """测试无效方向"""
        response = client.post('/api/2048/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        
        response = client.post(f'/api/2048/{game_id}/move',
                              data=json.dumps({'direction': 'INVALID'}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['changed'] is False
    
    def test_move_all_directions(self, client):
        """测试所有方向"""
        response = client.post('/api/2048/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        
        for direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            response = client.post(f'/api/2048/{game_id}/move',
                                  data=json.dumps({'direction': direction}),
                                  content_type='application/json')
            assert response.status_code == 200
    
    def test_reset(self, client):
        """测试重置"""
        # 创建游戏并移动
        response = client.post('/api/2048/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        
        client.post(f'/api/2048/{game_id}/move',
                   data=json.dumps({'direction': 'LEFT'}),
                   content_type='application/json')
        
        # 重置
        response = client.post(f'/api/2048/{game_id}/reset')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['score'] == 0
        assert data['game_over'] is False
        assert data['won'] is False
    
    def test_game_flow(self, client):
        """测试完整游戏流程"""
        # 创建游戏
        response = client.post('/api/2048/new')
        data = json.loads(response.data)
        game_id = data['game_id']
        
        # 进行多次移动
        for _ in range(10):
            for direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                response = client.post(f'/api/2048/{game_id}/move',
                                      data=json.dumps({'direction': direction}),
                                      content_type='application/json')
                assert response.status_code == 200
                data = json.loads(response.data)
                if data.get('game_over'):
                    break
            if data.get('game_over'):
                break
        
        # 游戏应该结束或者有分数
        assert 'score' in data
        assert 'game_over' in data
