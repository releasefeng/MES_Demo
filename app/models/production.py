from datetime import datetime
from app.extensions import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    unit = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.code} - {self.name}>'

class Process(db.Model):
    __tablename__ = 'processes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    sequence = db.Column(db.Integer, nullable=False)
    standard_time = db.Column(db.Float)  # 标准工时（分钟）
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Relationships
    product = db.relationship('Product', backref=db.backref('processes', lazy=True, order_by='Process.sequence'))
    
    def __repr__(self):
        return f'<Process {self.name} - Product {self.product_id}>'

class ProductionOrder(db.Model):
    __tablename__ = 'production_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, in_progress, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    product = db.relationship('Product', backref=db.backref('orders', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_orders', lazy=True))
    
    def __repr__(self):
        return f'<ProductionOrder {self.order_number} - Product {self.product_id}>'

class ProductionProgress(db.Model):
    __tablename__ = 'production_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('production_orders.id'), nullable=False)
    process_id = db.Column(db.Integer, db.ForeignKey('processes.id'), nullable=False)
    quantity_completed = db.Column(db.Integer, default=0)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = db.relationship('ProductionOrder', backref=db.backref('progress', lazy=True))
    process = db.relationship('Process', backref=db.backref('progress', lazy=True))
    operator = db.relationship('User', backref=db.backref('operated_progress', lazy=True))
    
    def __repr__(self):
        return f'<ProductionProgress {self.id} - Order {self.order_id} - Process {self.process_id}>' 