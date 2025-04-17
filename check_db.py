from app import create_app
from app.extensions import db
from app.models.test import TestData

app = create_app()

with app.app_context():
    # 获取TestData表的信息
    inspector = db.inspect(db.engine)
    columns = inspector.get_columns('test_data')
    print("\nTestData表结构:")
    for column in columns:
        print(f"列名: {column['name']}, 类型: {column['type']}, 可空: {column.get('nullable', True)}") 