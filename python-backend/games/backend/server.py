"""
Flask Web 服务器
"""
from flask import Flask, jsonify, request, send_from_directory
import os
import uuid

from snake import game_manager as snake_manager
from tetris import tetris_manager
from game2048 import game_2048_manager

app = Flask(__name__, static_folder='../frontend')


# ========== 贪吃蛇 API ==========

@app.route('/api/snake/new', methods=['POST'])
def snake_new():
    """创建新游戏"""
    game_id = str(uuid.uuid4())[:8]
    game = snake_manager.create_game(game_id)
    return jsonify({'game_id': game_id, 'state': game.get_state()})


@app.route('/api/snake/<game_id>/state', methods=['GET'])
def snake_state(game_id):
    """获取游戏状态"""
    game = snake_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    return jsonify(game.get_state())


@app.route('/api/snake/<game_id>/move', methods=['POST'])
def snake_move(game_id):
    """改变方向"""
    game = snake_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.get_json()
    direction = data.get('direction', '')
    game.change_direction(direction)
    return jsonify(game.get_state())


@app.route('/api/snake/<game_id>/step', methods=['POST'])
def snake_step(game_id):
    """前进一步"""
    game = snake_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    game.step()
    return jsonify(game.get_state())


@app.route('/api/snake/<game_id>/reset', methods=['POST'])
def snake_reset(game_id):
    """重置游戏"""
    game = snake_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    game.reset()
    return jsonify(game.get_state())


# ========== 俄罗斯方块 API ==========

@app.route('/api/tetris/new', methods=['POST'])
def tetris_new():
    """创建新游戏"""
    game_id = str(uuid.uuid4())[:8]
    game = tetris_manager.create_game(game_id)
    return jsonify({'game_id': game_id, 'state': game.get_state()})


@app.route('/api/tetris/<game_id>/state', methods=['GET'])
def tetris_state(game_id):
    """获取游戏状态"""
    game = tetris_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    return jsonify(game.get_state())


@app.route('/api/tetris/<game_id>/move', methods=['POST'])
def tetris_move(game_id):
    """移动方块"""
    game = tetris_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.get_json()
    dx = data.get('dx', 0)
    dy = data.get('dy', 0)
    game.move(dx, dy)
    return jsonify(game.get_state())


@app.route('/api/tetris/<game_id>/rotate', methods=['POST'])
def tetris_rotate(game_id):
    """旋转方块"""
    game = tetris_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    game.rotate()
    return jsonify(game.get_state())


@app.route('/api/tetris/<game_id>/drop', methods=['POST'])
def tetris_drop(game_id):
    """下落一步"""
    game = tetris_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    game.drop()
    return jsonify(game.get_state())


@app.route('/api/tetris/<game_id>/hard_drop', methods=['POST'])
def tetris_hard_drop(game_id):
    """快速下落"""
    game = tetris_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    game.hard_drop()
    return jsonify(game.get_state())


@app.route('/api/tetris/<game_id>/pause', methods=['POST'])
def tetris_pause(game_id):
    """暂停/继续"""
    game = tetris_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    game.toggle_pause()
    return jsonify(game.get_state())


@app.route('/api/tetris/<game_id>/reset', methods=['POST'])
def tetris_reset(game_id):
    """重置游戏"""
    game = tetris_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    game.reset()
    return jsonify(game.get_state())


# ========== 2048 API ==========

@app.route('/api/2048/new', methods=['POST'])
def game2048_new():
    """创建新游戏"""
    game_id = str(uuid.uuid4())[:8]
    data = request.get_json(silent=True) or {}
    size = data.get('size', 4)
    game = game_2048_manager.create_game(game_id, size)
    return jsonify({'game_id': game_id, 'state': game.get_state()})


@app.route('/api/2048/<game_id>/state', methods=['GET'])
def game2048_state(game_id):
    """获取游戏状态"""
    game = game_2048_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    return jsonify(game.get_state())


@app.route('/api/2048/<game_id>/move', methods=['POST'])
def game2048_move(game_id):
    """执行移动"""
    game = game_2048_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.get_json(silent=True) or {}
    direction = data.get('direction', '')
    changed = game.move(direction)
    return jsonify({'changed': changed, **game.get_state()})


@app.route('/api/2048/<game_id>/reset', methods=['POST'])
def game2048_reset(game_id):
    """重置游戏"""
    game = game_2048_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    game.reset()
    return jsonify(game.get_state())


# ========== 静态文件 ==========

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../frontend', path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
