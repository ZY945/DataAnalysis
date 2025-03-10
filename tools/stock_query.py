import adata
import pandas as pd
from datetime import datetime, timedelta

class StockQuery:
    def __init__(self):
        pass
        
    def get_stock_data(self, stock_code, start_date=None, end_date=None):
        """获取股票历史数据"""
        try:
            # 如果没有指定日期，默认查询近一年
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
                
            # 获取股票数据
            df = adata.stock.market.get_market(
                stock_code=stock_code,
                start_date=start_date,
                k_type=1  # 日K线
            )
            
            # 打印数据结构以便调试
            print(f"查询股票 {stock_code} 的数据:")
            print("数据类型:", type(df))
            print("数据列名:", df.columns.tolist() if isinstance(df, pd.DataFrame) else "不是DataFrame")
            
            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                raise Exception(f"未找到股票代码 {stock_code} 的数据")
            
            # 根据 adata 文档，返回的列名应该是:
            # trade_time, open, close, high, low, volume, amount, amplitude, 
            # change_percent, change_amount, turnover, trade_date
            
            # 处理数据
            df = df.sort_values('trade_date')  # 使用 trade_date 作为日期列
            result = {
                'dates': df['trade_date'].tolist(),
                'prices': {
                    'open': df['open'].tolist(),
                    'close': df['close'].tolist(),
                    'high': df['high'].tolist(),
                    'low': df['low'].tolist()
                },
                'volumes': df['volume'].tolist()
            }
            
            return result
            
        except Exception as e:
            print(f"获取股票 {stock_code} 数据失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise Exception(f"获取股票 {stock_code} 数据失败: {str(e)}")

    def get_stocks_data(self, stock_codes, start_date=None, end_date=None):
        """获取多个股票的历史数据"""
        result = {}
        errors = []
        
        for code in stock_codes:
            try:
                data = self.get_stock_data(code, start_date, end_date)
                result[code] = data
            except Exception as e:
                print(f"获取股票 {code} 数据失败: {str(e)}")
                result[code] = None
                errors.append(f"股票 {code}: {str(e)}")
        
        if all(v is None for v in result.values()):
            error_msg = "\n".join(errors)
            raise Exception(f"所有股票数据获取失败:\n{error_msg}")
            
        return result 