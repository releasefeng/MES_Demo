from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api/v1')

from app.api import routes, auth  # 确保导入所有路由模块 