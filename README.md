一个基于Python Flask的简单制造执行系统(MES)。

## 功能特性

- 生产订单管理
- 工序管理
- 生产计划
- 基础数据管理

## 安装步骤

1. 克隆项目到本地
2. 创建虚拟环境：
   ```bash
   python -m venv venv
   ```
3. 激活虚拟环境：
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
5. 初始化数据库：
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```
6. 运行应用：
   ```bash
   flask run
   ```

## 项目结构

```
mes-system/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── templates/
│   └── static/
├── config.py
├── requirements.txt
└── run.py
``` 
