from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.production import Product, ProductionOrder, ProductionProgress, Process
from app.extensions import db
from datetime import datetime

bp = Blueprint('production', __name__, url_prefix='/production')

@bp.route('/orders')
@login_required
def orders():
    orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).all()
    return render_template('production/orders.html', orders=orders)

@bp.route('/order/new', methods=['GET', 'POST'])
@login_required
def new_order():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        start_time = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        
        # 生成订单号
        order_number = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        order = ProductionOrder(
            order_number=order_number,
            product_id=product_id,
            quantity=quantity,
            start_time=start_time,
            created_by=current_user.id
        )
        
        db.session.add(order)
        db.session.commit()
        
        # 创建生产进度记录
        processes = Process.query.filter_by(product_id=product_id).order_by(Process.sequence).all()
        for process in processes:
            progress = ProductionProgress(
                order_id=order.id,
                process_id=process.id
            )
            db.session.add(progress)
        
        db.session.commit()
        flash('生产订单创建成功')
        return redirect(url_for('production.orders'))
    
    products = Product.query.all()
    return render_template('production/new_order.html', products=products)

@bp.route('/order/<int:id>')
@login_required
def order_detail(id):
    order = ProductionOrder.query.get_or_404(id)
    progress = ProductionProgress.query.filter_by(order_id=id).order_by(
        Process.sequence
    ).join(Process).all()
    return render_template('production/order_detail.html', order=order, progress=progress)

@bp.route('/order/<int:id>/start')
@login_required
def start_order(id):
    order = ProductionOrder.query.get_or_404(id)
    if order.status == 'pending':
        order.status = 'in_progress'
        order.start_time = datetime.utcnow()
        db.session.commit()
        flash('生产订单已开始')
    return redirect(url_for('production.order_detail', id=id))

@bp.route('/progress/update', methods=['POST'])
@login_required
def update_progress():
    progress_id = request.form.get('progress_id')
    quantity = request.form.get('quantity')
    
    progress = ProductionProgress.query.get_or_404(progress_id)
    
    if not progress.start_time:
        progress.start_time = datetime.utcnow()
        progress.status = 'in_progress'
        progress.operator_id = current_user.id
    
    progress.quantity_completed = quantity
    
    if int(quantity) >= progress.order.quantity:
        progress.status = 'completed'
        progress.end_time = datetime.utcnow()
        
        # 检查是否所有工序都完成
        all_completed = all(p.status == 'completed' for p in progress.order.progress)
        if all_completed:
            progress.order.status = 'completed'
            progress.order.end_time = datetime.utcnow()
    
    db.session.commit()
    flash('进度更新成功')
    return redirect(url_for('production.order_detail', id=progress.order_id)) 