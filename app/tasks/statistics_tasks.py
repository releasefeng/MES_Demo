from app.services.statistics_service import StatisticsService
from datetime import datetime, timedelta

def run_daily_statistics():
    """运行每日良率统计"""
    # 统计昨天的数据
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    StatisticsService.create_daily_statistics(yesterday)

def run_weekly_statistics():
    """运行每周良率统计"""
    # 获取上周的任意一天
    last_week = datetime.utcnow().date() - timedelta(days=7)
    StatisticsService.create_weekly_statistics(last_week)

def run_monthly_statistics():
    """运行每月良率统计"""
    # 获取上月的任意一天
    today = datetime.utcnow().date()
    if today.month == 1:
        last_month = today.replace(year=today.year-1, month=12, day=1)
    else:
        last_month = today.replace(month=today.month-1, day=1)
    StatisticsService.create_monthly_statistics(last_month) 