from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.production import ProductionOrder, ProductionProgress
from sqlalchemy import func
from app.extensions import db

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    # 获取生产订单统计
    total_orders = ProductionOrder.query.count()
    pending_orders = ProductionOrder.query.filter_by(status='pending').count()
    in_progress_orders = ProductionOrder.query.filter_by(status='in_progress').count()
    completed_orders = ProductionOrder.query.filter_by(status='completed').count()
    
    # 获取最近的生产订单
    recent_orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).limit(5).all()
    
    # 获取当前用户的任务
    if current_user.role == 'operator':
        user_tasks = ProductionProgress.query.filter_by(
            operator_id=current_user.id,
            status='in_progress'
        ).all()
    else:
        user_tasks = []
    
    return render_template('main/index.html',
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         in_progress_orders=in_progress_orders,
                         completed_orders=completed_orders,
                         recent_orders=recent_orders,
                         user_tasks=user_tasks) 