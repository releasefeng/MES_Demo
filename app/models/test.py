from datetime import datetime
from app import db

class TestData(db.Model):
    __tablename__ = 'test_data'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('production_orders.id'), nullable=False)
    process_id = db.Column(db.Integer, db.ForeignKey('processes.id'), nullable=False)
    sn = db.Column(db.String(100), nullable=False)
    test_item = db.Column(db.String(100), nullable=False)
    test_value = db.Column(db.String(100), nullable=False)
    test_result = db.Column(db.String(20), nullable=False)  # 合格/不合格
    test_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tester = db.Column(db.String(50), nullable=False)
    equipment_code = db.Column(db.String(50))
    remarks = db.Column(db.Text)

    # 关联关系
    order = db.relationship('ProductionOrder', backref=db.backref('test_data', lazy=True))
    process = db.relationship('Process', backref=db.backref('test_data', lazy=True))

    def __repr__(self):
        return f'<TestData {self.id} - Order {self.order_id} - Process {self.process_id}>' 