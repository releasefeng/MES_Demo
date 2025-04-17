from app.extensions import db
from datetime import datetime

class YieldStatistics(db.Model):
    """良率统计模型"""
    __tablename__ = 'yield_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('production_order.id'), nullable=False)
    
    total_count = db.Column(db.Integer, default=0)  # 总数
    pass_count = db.Column(db.Integer, default=0)   # 合格数
    fail_count = db.Column(db.Integer, default=0)   # 不合格数
    yield_rate = db.Column(db.Float, default=0.0)   # 良率
    
    start_time = db.Column(db.DateTime, nullable=False)  # 统计开始时间
    end_time = db.Column(db.DateTime, nullable=False)    # 统计结束时间
    statistics_type = db.Column(db.String(20), nullable=False)  # 统计类型：daily, weekly, monthly
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    product = db.relationship('Product', backref='yield_statistics')
    process = db.relationship('Process', backref='yield_statistics')
    order = db.relationship('ProductionOrder', backref='yield_statistics')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'process_id': self.process_id,
            'order_id': self.order_id,
            'total_count': self.total_count,
            'pass_count': self.pass_count,
            'fail_count': self.fail_count,
            'yield_rate': round(self.yield_rate, 2),
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'statistics_type': self.statistics_type,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'product_name': self.product.name if self.product else None,
            'process_name': self.process.name if self.process else None,
            'order_number': self.order.order_number if self.order else None
        } 