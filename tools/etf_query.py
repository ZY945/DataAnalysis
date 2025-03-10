import adata
import pandas as pd
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

class ETFQuery:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # 初始化时检查环境
        # self._check_environment()
        
    def _check_environment(self):
        """检查运行环境"""
        try:
            self.logger.info(f"adata 版本: {adata.__version__}")
            
            # 检查 py_mini_racer
            import py_mini_racer
            racer = py_mini_racer.MiniRacer()
            # 测试 JS 引擎
            result = racer.eval('1+1')
            self.logger.info(f"py_mini_racer 测试成功: 1+1 = {result}")
            
        except ImportError as e:
            self.logger.error(f"依赖库导入失败: {str(e)}")
            raise Exception("请先安装必要的依赖库")
        except Exception as e:
            self.logger.error(f"环境检查失败: {str(e)}")
            raise Exception("环境检查失败，请确保所有依赖正确安装")
        
    def get_etf_data(self, etf_code, start_date=None, end_date=None):
        """获取ETF历史数据"""
        try:
            self.logger.info(f"开始获取ETF {etf_code} 的数据")
            
            # 如果没有指定日期，默认查询近一年
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
                
            self.logger.debug(f"查询参数: start_date={start_date}, end_date={end_date}")
            
            # 获取ETF数据
            self.logger.debug(f"调用 adata API 获取数据...")
            try:
                df = adata.fund.market.get_market_etf(
                    fund_code=etf_code,
                    start_date=start_date,
                    k_type=1
                )
            except Exception as api_error:
                self.logger.error(f"API调用失败: {str(api_error)}")
                # 尝试使用备用方法
                self.logger.info("尝试使用备用方法获取数据...")
                df = adata.fund.market.get_market_etf(
                    fund_code=str(etf_code),  # 确保是字符串
                    start_date=start_date,
                    k_type="1"  # 尝试字符串类型
                )
            
            # 打印数据结构
            self.logger.debug(f"数据类型: {type(df)}")
            if isinstance(df, pd.DataFrame):
                self.logger.debug(f"数据列名: {df.columns.tolist()}")
                self.logger.debug(f"数据行数: {len(df)}")
                self.logger.debug(f"数据示例:\n{df.head()}")
            else:
                self.logger.warning(f"返回的数据不是DataFrame: {df}")
            
            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                raise Exception(f"未找到ETF代码 {etf_code} 的数据")
            
            # 处理数据
            self.logger.debug("开始处理数据...")
            df = df.sort_values('trade_date')
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
            
            self.logger.info(f"成功获取ETF {etf_code} 的数据，共 {len(df)} 条记录")
            return result
            
        except Exception as e:
            self.logger.error(f"获取ETF {etf_code} 数据失败: {str(e)}")
            import traceback
            self.logger.error(f"错误堆栈:\n{traceback.format_exc()}")
            raise
            
    def get_etfs_data(self, etf_codes, start_date=None, end_date=None):
        """获取多个ETF的历史数据"""
        self.logger.info(f"开始获取多个ETF数据: {etf_codes}")
        result = {}
        errors = []
        
        for code in etf_codes:
            try:
                data = self.get_etf_data(code, start_date, end_date)
                result[code] = data
            except Exception as e:
                self.logger.error(f"获取ETF {code} 数据失败: {str(e)}")
                result[code] = None
                errors.append(f"ETF {code}: {str(e)}")
        
        if all(v is None for v in result.values()):
            error_msg = "\n".join(errors)
            self.logger.error(f"所有ETF数据获取失败:\n{error_msg}")
            raise Exception(f"所有ETF数据获取失败:\n{error_msg}")
            
        return result 