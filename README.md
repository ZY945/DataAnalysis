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
./venv/bin/python3 app.py     
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

# 数据来源说明

## 大A股市，ETF数据来源
数据来源: https://github.com/1nchaos/adata


# 贡献
欢迎大家贡献代码，共同完善这个项目。
## 贡献
1. 提交代码
2. 提交PR
3. 审核通过后，合并到主分支
4. 发布新版本

## 生成requirements.txt
# 安装
pip install pipreqs
# 在当前目录生成
pipreqs . --encoding=utf8 --force
## 和 akshare 的依赖有冲突
https://github.com/1nchaos/adata/issues/122

下载https://github.com/sqreen/PyMiniRacer/files/7575004/libmini_racer.dylib.zip
这里已经下载放入source文件夹里了
解压后，将libmini_racer.dylib放到site-packages的py_mini_racer目录下
