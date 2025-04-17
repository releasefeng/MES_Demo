import requests
import json
from datetime import datetime
import csv
import os
import pandas as pd
from typing import List, Dict, Optional

# API配置
BASE_URL = 'http://localhost:5000'  # MES系统的基础URL

def get_token():
    """获取认证token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/login",
        json={"username": "admin", "password": "admin"}
    )
    return response.json()['token']

def validate_test_data(test_data: Dict) -> List[str]:
    """验证测试数据的完整性和格式"""
    errors = []
    required_fields = ['order_id', 'process_id', 'sn', 'test_item', 'test_value', 'test_result']
    
    # 检查必填字段
    for field in required_fields:
        if field not in test_data:
            errors.append(f"缺少必填字段: {field}")
    
    # 验证数据类型
    if 'test_value' in test_data and not isinstance(test_data['test_value'], (str, int, float)):
        errors.append("test_value 必须是数字或字符串类型")
    
    # 验证测试结果格式
    if 'test_result' in test_data and test_data['test_result'] not in ['合格', '不合格']:
        errors.append("test_result 必须是 '合格' 或 '不合格'")
    
    return errors

def upload_test_data(token: str, test_data: Dict) -> bool:
    """上传测试数据"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 验证数据
    errors = validate_test_data(test_data)
    if errors:
        print("数据验证失败:")
        for error in errors:
            print(f"- {error}")
        return False
    
    response = requests.post(
        f"{BASE_URL}/api/v1/test/data",
        headers=headers,
        json=test_data
    )
    
    if response.status_code == 201:
        print(f"数据上传成功: {response.json()}")
        return True
    else:
        print(f"数据上传失败: {response.text}")
        return False

def get_test_data(token: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
    """获取测试数据"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    params = {}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    
    response = requests.get(
        f"{BASE_URL}/api/v1/test/data",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"获取数据失败: {response.text}")
        return []

def calculate_yield_rate(test_data: List[Dict]) -> Dict:
    """计算良率统计"""
    total = len(test_data)
    if total == 0:
        return {
            "total": 0,
            "pass": 0,
            "fail": 0,
            "yield_rate": 0
        }
    
    passed = sum(1 for item in test_data if item['test_result'] == '合格')
    failed = total - passed
    
    return {
        "total": total,
        "pass": passed,
        "fail": failed,
        "yield_rate": round(passed / total * 100, 2)
    }

def export_to_csv(data: List[Dict], filename: str):
    """导出数据到CSV文件"""
    if not data:
        print("没有数据可导出")
        return
    
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"数据已成功导出到: {filename}")
    except Exception as e:
        print(f"导出数据失败: {str(e)}")

def batch_upload_from_csv(token: str, csv_file: str) -> Dict:
    """从CSV文件批量上传测试数据"""
    results = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "errors": []
    }
    
    try:
        df = pd.read_csv(csv_file)
        results["total"] = len(df)
        
        for _, row in df.iterrows():
            test_data = row.to_dict()
            if upload_test_data(token, test_data):
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"行 {_ + 2} 上传失败")
    
    except Exception as e:
        print(f"批量上传过程中出错: {str(e)}")
    
    return results

def main():
    try:
        # 1. 获取token
        token = get_token()
        print("认证成功！")
        
        # 2. 准备测试数据
        test_data = {
            "order_id": 1,              # 订单ID
            "process_id": 1,            # 工序ID
            "sn": "TEST20240101001",    # 序列号
            "test_item": "尺寸检测",     # 测试项目
            "test_value": "98.5",       # 测试值
            "test_result": "合格",       # 测试结果
            "equipment_code": "EQ001",   # 设备编号
            "remarks": "正常检测",        # 备注
            "tester": "admin"           # 测试人员
        }
        
        # 3. 上传单条测试数据
        print("\n正在上传测试数据...")
        print(f"测试数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        upload_test_data(token, test_data)
        
        # 4. 获取今日测试数据
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"\n获取{today}的测试数据...")
        test_records = get_test_data(token, start_date=today)
        
        # 5. 计算良率
        yield_stats = calculate_yield_rate(test_records)
        print("\n良率统计:")
        print(f"总数: {yield_stats['total']}")
        print(f"合格: {yield_stats['pass']}")
        print(f"不合格: {yield_stats['fail']}")
        print(f"良率: {yield_stats['yield_rate']}%")
        
        # 6. 导出数据
        if test_records:
            export_filename = f"test_data_{today}.csv"
            export_to_csv(test_records, export_filename)
        
        # 7. 演示批量上传（如果有CSV文件）
        csv_file = "batch_test_data.csv"
        if os.path.exists(csv_file):
            print("\n开始批量上传数据...")
            results = batch_upload_from_csv(token, csv_file)
            print(f"批量上传结果:")
            print(f"总数: {results['total']}")
            print(f"成功: {results['success']}")
            print(f"失败: {results['failed']}")
            if results['errors']:
                print("错误详情:")
                for error in results['errors']:
                    print(f"- {error}")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main() 