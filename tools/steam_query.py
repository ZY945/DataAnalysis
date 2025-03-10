import requests
import json
from datetime import datetime, timedelta

class SteamQuery:
    def __init__(self):
        self.base_url = "https://steamdt.com/api/v2"
        
    def get_item_data(self, item_name, start_date=None, end_date=None):
        """获取饰品历史数据"""
        try:
            # 如果没有指定日期，默认查询近一年
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
                
            # 构造请求参数
            params = {
                'name': item_name,
                'start_date': start_date,
                'end_date': end_date
            }
            
            # 发送请求
            response = requests.get(f"{self.base_url}/market/item/price_history", params=params)
            response.raise_for_status()  # 检查响应状态
            
            data = response.json()
            if not data.get('success'):
                raise Exception(data.get('message', '未知错误'))
                
            # 处理数据
            history = data['data']['price_history']
            result = {
                'dates': [item['time'] for item in history],
                'prices': {
                    'price': [item['price'] for item in history],
                    'volume': [item['volume'] for item in history]
                }
            }
            
            return result
            
        except requests.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"获取饰品 {item_name} 数据失败: {str(e)}")
            
    def get_items_data(self, item_names, start_date=None, end_date=None):
        """获取多个饰品的历史数据"""
        result = {}
        errors = []
        
        for name in item_names:
            try:
                data = self.get_item_data(name, start_date, end_date)
                result[name] = data
            except Exception as e:
                print(f"获取饰品 {name} 数据失败: {str(e)}")
                result[name] = None
                errors.append(f"饰品 {name}: {str(e)}")
        
        if all(v is None for v in result.values()):
            error_msg = "\n".join(errors)
            raise Exception(f"所有饰品数据获取失败:\n{error_msg}")
            
        return result 