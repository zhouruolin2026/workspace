# Python 游戏后端

## 项目结构
```
games/
├── backend/
│   ├── snake.py          # 贪吃蛇游戏逻辑
│   ├── tetris.py         # 俄罗斯方块游戏逻辑
│   ├── server.py         # Flask Web 服务器
│   └── tests/
│       ├── test_snake.py      # 单元测试
│       ├── test_tetris.py     # 单元测试
│       └── test_integration.py # 系统测试
├── frontend/
│   ├── snake.html        # 贪吃蛇前端
│   └── tetris.html       # 俄罗斯方块前端
└── requirements.txt
```

## 安装依赖
```bash
pip install -r requirements.txt
```

## 运行测试
```bash
cd backend
python -m pytest tests/ -v
```

## 启动服务器
```bash
cd backend
python server.py
```

访问 http://localhost:5000
