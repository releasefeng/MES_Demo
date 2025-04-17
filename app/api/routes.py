from flask import jsonify, request
from app.api import bp
from app.api.auth import token_required, generate_token
from app.models.test import TestData
from app.models.production import ProductionOrder, Process, Product
from app.models.user import User
from app.extensions import db
from datetime import datetime

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Missing username or password'}), 401
    
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 401
    
    if user.check_password(data['password']):
        token = generate_token(user.id)
        return jsonify({'token': token})
    
    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/products', methods=['POST'])
@token_required
def create_product(current_user):
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['code', 'name', 'unit']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # 创建产品
    product = Product(
        code=data['code'],
        name=data['name'],
        description=data.get('description'),
        unit=data['unit']
    )
    
    try:
        db.session.add(product)
        db.session.commit()
        return jsonify({
            'message': 'Product created successfully',
            'id': product.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating product', 'error': str(e)}), 500

@bp.route('/processes', methods=['POST'])
@token_required
def create_process(current_user):
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['name', 'sequence', 'product_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # 验证产品是否存在
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'message': 'Invalid product_id'}), 400
    
    # 创建工序
    process = Process(
        name=data['name'],
        description=data.get('description'),
        sequence=data['sequence'],
        standard_time=data.get('standard_time'),
        product_id=data['product_id']
    )
    
    try:
        db.session.add(process)
        db.session.commit()
        return jsonify({
            'message': 'Process created successfully',
            'id': process.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating process', 'error': str(e)}), 500

@bp.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['product_id', 'quantity', 'order_number']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # 验证产品是否存在
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'message': 'Invalid product_id'}), 400
    
    # 创建订单
    order = ProductionOrder(
        order_number=data['order_number'],
        product_id=data['product_id'],
        quantity=data['quantity'],
        status='pending',
        created_by=current_user.id
    )
    
    try:
        db.session.add(order)
        db.session.commit()
        return jsonify({
            'message': 'Order created successfully',
            'id': order.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating order', 'error': str(e)}), 500

@bp.route('/test/data', methods=['POST', 'GET'])
@token_required
def test_data(current_user):
    if request.method == 'POST':
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['order_id', 'process_id', 'sn', 'test_item', 'test_value', 'test_result']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # 验证订单和工序是否存在
        order = ProductionOrder.query.get(data['order_id'])
        process = Process.query.get(data['process_id'])
        
        if not order or not process:
            return jsonify({'message': 'Invalid order_id or process_id'}), 400
        
        # 创建测试数据记录
        test_data = TestData(
            order_id=data['order_id'],
            process_id=data['process_id'],
            sn=data['sn'],
            test_item=data['test_item'],
            test_value=data['test_value'],
            test_result=data['test_result'],
            test_time=datetime.utcnow(),
            tester=current_user.username,
            equipment_code=data.get('equipment_code'),
            remarks=data.get('remarks')
        )
        
        try:
            db.session.add(test_data)
            db.session.commit()
            return jsonify({
                'message': 'Test data uploaded successfully',
                'test_id': test_data.id
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error uploading test data', 'error': str(e)}), 500
    else:
        # 获取查询参数
        order_id = request.args.get('order_id')
        process_id = request.args.get('process_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = TestData.query
        
        if order_id:
            query = query.filter_by(order_id=order_id)
        if process_id:
            query = query.filter_by(process_id=process_id)
        if start_date:
            query = query.filter(TestData.test_time >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(TestData.test_time <= datetime.strptime(end_date, '%Y-%m-%d'))
        
        # 获取数据
        test_data = query.order_by(TestData.test_time.desc()).all()
        
        # 格式化响应
        return jsonify({
            'data': [{
                'id': td.id,
                'order_id': td.order_id,
                'process_id': td.process_id,
                'test_item': td.test_item,
                'test_value': td.test_value,
                'test_result': td.test_result,
                'test_time': td.test_time.strftime('%Y-%m-%d %H:%M:%S'),
                'tester': td.tester,
                'equipment_code': td.equipment_code,
                'remarks': td.remarks
            } for td in test_data]
        }) 