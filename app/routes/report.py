from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models.production import ProductionOrder, ProductionProgress, Product, Process
from app.models.user import User
from app.extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta
import calendar

bp = Blueprint('report', __name__, url_prefix='/report')

@bp.route('/orders')
@login_required
def order_report():
    # 获取时间范围
    period = request.args.get('period', 'month')  # month, quarter, year
    end_date = datetime.now()
    
    if period == 'month':
        start_date = end_date.replace(day=1)
    elif period == 'quarter':
        quarter_start_month = ((end_date.month - 1) // 3) * 3 + 1
        start_date = end_date.replace(month=quarter_start_month, day=1)
    else:  # year
        start_date = end_date.replace(month=1, day=1)
    
    # 订单状态统计
    status_stats = db.session.query(
        ProductionOrder.status,
        func.count(ProductionOrder.id).label('count')
    ).filter(
        ProductionOrder.created_at.between(start_date, end_date)
    ).group_by(ProductionOrder.status).all()
    
    # 按产品统计订单数量
    product_stats = db.session.query(
        Product.name,
        func.count(ProductionOrder.id).label('order_count'),
        func.sum(ProductionOrder.quantity).label('total_quantity')
    ).join(ProductionOrder).filter(
        ProductionOrder.created_at.between(start_date, end_date)
    ).group_by(Product.id).all()
    
    return render_template('report/orders.html',
                         period=period,
                         start_date=start_date,
                         end_date=end_date,
                         status_stats=status_stats,
                         product_stats=product_stats)

@bp.route('/efficiency')
@login_required
def efficiency_report():
    # 获取时间范围
    days = int(request.args.get('days', 30))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 计算每个工序的平均完成时间
    process_stats = db.session.query(
        Process.name,
        func.avg(
            func.extract('epoch', ProductionProgress.end_time) -
            func.extract('epoch', ProductionProgress.start_time)
        ).label('avg_time'),
        func.count(ProductionProgress.id).label('count')
    ).join(ProductionProgress).filter(
        ProductionProgress.status == 'completed',
        ProductionProgress.start_time.between(start_date, end_date)
    ).group_by(Process.id).all()
    
    # 计算产品的平均生产周期
    product_cycle = db.session.query(
        Product.name,
        func.avg(
            func.extract('epoch', ProductionOrder.end_date) -
            func.extract('epoch', ProductionOrder.start_date)
        ).label('avg_cycle'),
        func.count(ProductionOrder.id).label('count')
    ).join(ProductionOrder).filter(
        ProductionOrder.status == 'completed',
        ProductionOrder.start_date.between(start_date, end_date)
    ).group_by(Product.id).all()
    
    return render_template('report/efficiency.html',
                         days=days,
                         start_date=start_date,
                         end_date=end_date,
                         process_stats=process_stats,
                         product_cycle=product_cycle)

@bp.route('/operators')
@login_required
def operator_report():
    # 获取时间范围
    period = request.args.get('period', 'month')
    end_date = datetime.now()
    
    if period == 'month':
        start_date = end_date.replace(day=1)
    elif period == 'quarter':
        quarter_start_month = ((end_date.month - 1) // 3) * 3 + 1
        start_date = end_date.replace(month=quarter_start_month, day=1)
    else:  # year
        start_date = end_date.replace(month=1, day=1)
    
    # 操作员工作量统计
    operator_stats = db.session.query(
        User.username,
        func.count(ProductionProgress.id).label('task_count'),
        func.sum(ProductionProgress.quantity_completed).label('total_quantity'),
        func.count(func.distinct(ProductionProgress.order_id)).label('order_count')
    ).join(ProductionProgress).filter(
        ProductionProgress.start_time.between(start_date, end_date)
    ).group_by(User.id).all()
    
    # 按工序类型统计
    process_stats = db.session.query(
        User.username,
        Process.name,
        func.count(ProductionProgress.id).label('count')
    ).join(ProductionProgress).join(Process).filter(
        ProductionProgress.start_time.between(start_date, end_date)
    ).group_by(User.id, Process.id).all()
    
    return render_template('report/operators.html',
                         period=period,
                         start_date=start_date,
                         end_date=end_date,
                         operator_stats=operator_stats,
                         process_stats=process_stats) 