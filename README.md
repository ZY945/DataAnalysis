# Flask Todo 应用

一个简单的待办事项Web应用，使用Flask实现前后端一体化。

## 项目结构

```
.
├── app.py              # Flask 应用主文件
├── requirements.txt    # 项目依赖
├── README.md          # 项目说明文档
└── templates          
    └── index.html     # 前端页面
```

## 环境配置

1. 创建虚拟环境
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

## 运行项目

1. 激活虚拟环境(如果尚未激活)
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. 启动应用
```bash
python app.py
```

3. 访问应用
打开浏览器访问 http://localhost:5000

## 功能特性

- 查看所有待办事项
- 添加新的待办事项
- 响应式界面设计

## 技术栈

- 后端：Flask
- 前端：HTML, CSS, JavaScript
- API：RESTful API

# 生成requirements.txt
# 先安装pipreqs
pip install pipreqs

# 然后在项目根目录运行
pipreqs ./ --encoding=utf8