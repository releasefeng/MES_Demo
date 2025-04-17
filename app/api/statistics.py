from flask import jsonify, request
from app.api import bp
from app.api.auth import token_required
from app.services.statistics_service import StatisticsService
from datetime import datetime

@bp.route('/statistics/yield/daily', methods=['POST'])
@token_required
def create_daily_statistics(current_user):
    """创建每日良率统计"""
    date_str = request.args.get('date')
    try:
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = None
        
        success = StatisticsService.create_daily_statistics(date)
        if success:
            return jsonify({'message': 'Daily statistics created successfully'}), 201
        else:
            return jsonify({'message': 'Error creating daily statistics'}), 500
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

@bp.route('/statistics/yield/weekly', methods=['POST'])
@token_required
def create_weekly_statistics(current_user):
    """创建每周良率统计"""
    date_str = request.args.get('date')
    try:
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = None
        
        success = StatisticsService.create_weekly_statistics(date)
        if success:
            return jsonify({'message': 'Weekly statistics created successfully'}), 201
        else:
            return jsonify({'message': 'Error creating weekly statistics'}), 500
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

@bp.route('/statistics/yield/monthly', methods=['POST'])
@token_required
def create_monthly_statistics(current_user):
    """创建每月良率统计"""
    date_str = request.args.get('date')
    try:
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = None
        
        success = StatisticsService.create_monthly_statistics(date)
        if success:
            return jsonify({'message': 'Monthly statistics created successfully'}), 201
        else:
            return jsonify({'message': 'Error creating monthly statistics'}), 500
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

@bp.route('/statistics/yield', methods=['GET'])
@token_required
def get_yield_statistics(current_user):
    """获取良率统计数据"""
    # 获取查询参数
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    product_id = request.args.get('product_id', type=int)
    process_id = request.args.get('process_id', type=int)
    statistics_type = request.args.get('type', 'daily')
    
    try:
        # 转换日期格式
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 获取统计数据
        statistics = StatisticsService.get_statistics(
            start_date=start_date,
            end_date=end_date,
            product_id=product_id,
            process_id=process_id,
            statistics_type=statistics_type
        )
        
        # 转换为字典格式
        result = [stat.to_dict() for stat in statistics]
        
        return jsonify({
            'data': result,
            'total': len(result)
        })
    
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400 