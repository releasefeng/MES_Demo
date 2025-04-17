from datetime import datetime, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models.statistics import YieldStatistics
from app.models.test import TestData

class StatisticsService:
    @staticmethod
    def calculate_yield_rate(pass_count, total_count):
        """计算良率"""
        return (pass_count / total_count * 100) if total_count > 0 else 0

    @staticmethod
    def create_daily_statistics(date=None):
        """创建每日良率统计"""
        if date is None:
            date = datetime.utcnow().date()
        
        start_time = datetime.combine(date, datetime.min.time())
        end_time = datetime.combine(date, datetime.max.time())
        
        # 获取当日所有测试数据的统计信息
        stats = db.session.query(
            TestData.product_id,
            TestData.process_id,
            TestData.order_id,
            func.count().label('total_count'),
            func.sum(case((TestData.test_result == '合格', 1), else_=0)).label('pass_count')
        ).filter(
            TestData.test_time.between(start_time, end_time)
        ).group_by(
            TestData.product_id,
            TestData.process_id,
            TestData.order_id
        ).all()
        
        for stat in stats:
            yield_stat = YieldStatistics(
                product_id=stat.product_id,
                process_id=stat.process_id,
                order_id=stat.order_id,
                total_count=stat.total_count,
                pass_count=stat.pass_count,
                fail_count=stat.total_count - stat.pass_count,
                yield_rate=StatisticsService.calculate_yield_rate(stat.pass_count, stat.total_count),
                start_time=start_time,
                end_time=end_time,
                statistics_type='daily'
            )
            db.session.add(yield_stat)
        
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error creating daily statistics: {str(e)}")
            return False

    @staticmethod
    def create_weekly_statistics(date=None):
        """创建每周良率统计"""
        if date is None:
            date = datetime.utcnow().date()
        
        # 计算本周的开始和结束时间
        start_time = datetime.combine(date - timedelta(days=date.weekday()), datetime.min.time())
        end_time = start_time + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        # 获取本周所有测试数据的统计信息
        stats = db.session.query(
            TestData.product_id,
            TestData.process_id,
            TestData.order_id,
            func.count().label('total_count'),
            func.sum(case((TestData.test_result == '合格', 1), else_=0)).label('pass_count')
        ).filter(
            TestData.test_time.between(start_time, end_time)
        ).group_by(
            TestData.product_id,
            TestData.process_id,
            TestData.order_id
        ).all()
        
        for stat in stats:
            yield_stat = YieldStatistics(
                product_id=stat.product_id,
                process_id=stat.process_id,
                order_id=stat.order_id,
                total_count=stat.total_count,
                pass_count=stat.pass_count,
                fail_count=stat.total_count - stat.pass_count,
                yield_rate=StatisticsService.calculate_yield_rate(stat.pass_count, stat.total_count),
                start_time=start_time,
                end_time=end_time,
                statistics_type='weekly'
            )
            db.session.add(yield_stat)
        
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error creating weekly statistics: {str(e)}")
            return False

    @staticmethod
    def create_monthly_statistics(date=None):
        """创建每月良率统计"""
        if date is None:
            date = datetime.utcnow().date()
        
        # 计算本月的开始和结束时间
        start_time = datetime.combine(date.replace(day=1), datetime.min.time())
        if date.month == 12:
            end_time = datetime.combine(date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1), datetime.max.time())
        else:
            end_time = datetime.combine(date.replace(month=date.month + 1, day=1) - timedelta(days=1), datetime.max.time())
        
        # 获取本月所有测试数据的统计信息
        stats = db.session.query(
            TestData.product_id,
            TestData.process_id,
            TestData.order_id,
            func.count().label('total_count'),
            func.sum(case((TestData.test_result == '合格', 1), else_=0)).label('pass_count')
        ).filter(
            TestData.test_time.between(start_time, end_time)
        ).group_by(
            TestData.product_id,
            TestData.process_id,
            TestData.order_id
        ).all()
        
        for stat in stats:
            yield_stat = YieldStatistics(
                product_id=stat.product_id,
                process_id=stat.process_id,
                order_id=stat.order_id,
                total_count=stat.total_count,
                pass_count=stat.pass_count,
                fail_count=stat.total_count - stat.pass_count,
                yield_rate=StatisticsService.calculate_yield_rate(stat.pass_count, stat.total_count),
                start_time=start_time,
                end_time=end_time,
                statistics_type='monthly'
            )
            db.session.add(yield_stat)
        
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error creating monthly statistics: {str(e)}")
            return False

    @staticmethod
    def get_statistics(start_date=None, end_date=None, product_id=None, process_id=None, statistics_type='daily'):
        """获取良率统计数据"""
        query = YieldStatistics.query
        
        if start_date:
            query = query.filter(YieldStatistics.start_time >= start_date)
        if end_date:
            query = query.filter(YieldStatistics.end_time <= end_date)
        if product_id:
            query = query.filter(YieldStatistics.product_id == product_id)
        if process_id:
            query = query.filter(YieldStatistics.process_id == process_id)
        
        query = query.filter(YieldStatistics.statistics_type == statistics_type)
        
        return query.order_by(YieldStatistics.start_time.desc()).all() 