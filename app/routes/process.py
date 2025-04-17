from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.production import Product, Process, ProductionOrder
from app.models.test import TestData
from app.extensions import db
from datetime import datetime, timedelta

bp = Blueprint('process', __name__, url_prefix='/process')

@bp.route('/products')
@login_required
def products():
    products = Product.query.all()
    return render_template('process/products.html', products=products)

@bp.route('/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        description = request.form.get('description')
        unit = request.form.get('unit')
        
        if Product.query.filter_by(code=code).first():
            flash('产品编码已存在')
            return redirect(url_for('process.new_product'))
        
        product = Product(
            code=code,
            name=name,
            description=description,
            unit=unit
        )
        
        db.session.add(product)
        db.session.commit()
        flash('产品创建成功')
        return redirect(url_for('process.products'))
    
    return render_template('process/new_product.html')

@bp.route('/product/<int:id>')
@login_required
def product_detail(id):
    product = Product.query.get_or_404(id)
    processes = Process.query.filter_by(product_id=id).order_by(Process.sequence).all()
    return render_template('process/product_detail.html', product=product, processes=processes)

@bp.route('/product/<int:id>/process/new', methods=['GET', 'POST'])
@login_required
def new_process(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        sequence = request.form.get('sequence')
        standard_time = request.form.get('standard_time')
        
        process = Process(
            name=name,
            description=description,
            sequence=sequence,
            standard_time=standard_time,
            product_id=id
        )
        
        db.session.add(process)
        db.session.commit()
        flash('工序创建成功')
        return redirect(url_for('process.product_detail', id=id))
    
    return render_template('process/new_process.html', product=product)

@bp.route('/process/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_process(id):
    process = Process.query.get_or_404(id)
    
    if request.method == 'POST':
        process.name = request.form.get('name')
        process.description = request.form.get('description')
        process.sequence = request.form.get('sequence')
        process.standard_time = request.form.get('standard_time')
        
        db.session.commit()
        flash('工序更新成功')
        return redirect(url_for('process.product_detail', id=process.product_id))
    
    return render_template('process/edit_process.html', process=process)

@bp.route('/upload_test_data', methods=['GET', 'POST'])
@login_required
def upload_test_data():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        process_id = request.form.get('process_id')
        test_item = request.form.get('test_item')
        test_value = request.form.get('test_value')
        test_result = request.form.get('test_result')
        equipment_code = request.form.get('equipment_code')
        remarks = request.form.get('remarks')

        # Validate required fields
        if not all([order_id, process_id, test_item, test_value, test_result]):
            flash('请填写所有必填字段', 'danger')
            return redirect(url_for('process.upload_test_data'))

        try:
            # Create new test data record
            test_data = TestData(
                order_id=order_id,
                process_id=process_id,
                test_item=test_item,
                test_value=test_value,
                test_result=test_result,
                equipment_code=equipment_code,
                remarks=remarks,
                test_time=datetime.now(),
                tester=current_user.username
            )
            db.session.add(test_data)
            db.session.commit()
            flash('测试数据上传成功', 'success')
            return redirect(url_for('process.test_data'))
        except Exception as e:
            db.session.rollback()
            flash('测试数据上传失败：' + str(e), 'danger')
            return redirect(url_for('process.upload_test_data'))

    # GET request - display the form
    orders = ProductionOrder.query.filter(
        ProductionOrder.status.in_(['进行中', '已完成'])
    ).order_by(ProductionOrder.created_at.desc()).all()
    
    processes = Process.query.order_by(Process.sequence.asc()).all()
    
    return render_template('process/upload_test_data.html', 
                         orders=orders, 
                         processes=processes)

@bp.route('/test/data')
@login_required
def test_data():
    # Get filter parameters
    order_id = request.args.get('order_id')
    process_id = request.args.get('process_id')
    test_result = request.args.get('test_result')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Base query
    query = TestData.query

    # Apply filters
    if order_id:
        query = query.filter(TestData.order_id == order_id)
    if process_id:
        query = query.filter(TestData.process_id == process_id)
    if test_result:
        query = query.filter(TestData.test_result == test_result)
    if start_date:
        query = query.filter(TestData.test_time >= start_date)
    if end_date:
        query = query.filter(TestData.test_time <= end_date)

    # Get test data with pagination
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(TestData.test_time.desc()).paginate(
        page=page, per_page=10, error_out=False)
    test_data = pagination.items

    # Get all orders and processes for filter dropdowns
    orders = ProductionOrder.query.all()
    processes = Process.query.all()

    return render_template('process/test_data.html',
                         test_data=test_data,
                         pagination=pagination,
                         orders=orders,
                         processes=processes) 