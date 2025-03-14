import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import os
from crawler_utils import CrawlerUtils
import logging
from selenium.webdriver.common.by import By
import re
import time

class FundQuery:
    BASE_URL = "https://m.dayfund.cn/fundpre/{}.html"
    REAL_TIME_URL = "https://m.dayfund.cn/ajs/ajaxdata.shtml"
    
    @staticmethod
    def get_real_time_value(fund_code):
        """
        获取基金实时估值
        """
        headers = {
            'sec-ch-ua-platform': 'Android',
            'Referer': f'https://m.dayfund.cn/fundinfo/{fund_code}.html',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36',
            'Accept': '*/*',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?1'
        }
        
        params = {
            'showtype': 'getfundvalue',
            'fundcode': fund_code,
            't': '11'
        }
        
        try:
            response = requests.get(FundQuery.REAL_TIME_URL, headers=headers, params=params)
            response.raise_for_status()
            
            # [0]: 昨日净值日期 (2025-03-13)
            # [1], [2]: 昨日净值 (1.0825)
            # [3], [4]: 昨日净值涨跌额和涨跌幅 (-0.0206, -1.87%)
            # [5], [6]: 今日实时估值涨跌幅和涨跌额 (1.79%, 0.0194)
            # [7]: 今日实时估值 (1.1019)
            # [8]: 昨日净值 (1.1031)
            # [9], [10]: 实时估值更新时间 (2025-03-14 11:30:00)
            data = response.text.split('|')
            if len(data) >= 10:
                return {
                    # 实时估值数据
                    'real_time': {
                        'value': data[7],        # 今日实时估值
                        'change': data[6],       # 估算涨跌额
                        'change_percent': data[5],# 估算涨跌幅
                        'update_time': f"{data[9]} {data[10]}"
                    },
                    # 最新净值数据
                    'latest_net': {
                        'value': data[1],        # 昨日净值
                        'date': data[0],         # 净值日期
                        'change': data[3],       # 净值涨跌额
                        'change_percent': data[4] # 净值涨跌幅
                    }
                }
            return None
        except Exception as e:
            logging.error(f"获取实时估值失败: {fund_code}, 错误: {str(e)}")
            return None
    
    @staticmethod
    def get_fund_info(fund_code):
        """
        获取基金信息
        """
        url = FundQuery.BASE_URL.format(fund_code)
        html_content = CrawlerUtils.get_html_by_requests(url)
        
        if not html_content:
            logging.error(f"获取基金信息失败: {fund_code}")
            return None
        
        # 获取实时估值
        real_time_data = FundQuery.get_real_time_value(fund_code)
        
        # 解析其他数据
        fund_info = FundQuery._parse_fund_info(html_content)
        
        if fund_info and real_time_data:
            fund_info['real_time_value'] = real_time_data
            
        return fund_info
    
    @staticmethod
    def _parse_fund_info(html_content):
        """
        解析基金HTML内容
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 1. 获取实时估值
            real_time_value = soup.find('span', id='fvr_val').text.strip()
            
            # 2. 获取重仓股数据
            stock_table = soup.find_all('table')[0]
            stock_rows = stock_table.find_all('tr')[1:-1]  # 跳过表头和表尾
            
            holdings = []
            for row in stock_rows:
                cols = row.find_all('td')
                holding = {
                    'stock_code': cols[0].text.strip(),
                    'stock_name': cols[1].text.strip(),
                    'position_ratio': cols[2].text.strip(),
                    'change_percent': cols[3].text.strip(),
                    'contribution': cols[4].text.strip()
                }
                holdings.append(holding)
            
            # 3. 获取历史对照数据
            history_table = soup.find_all('table')[1]
            history_rows = history_table.find_all('tr')[1:]  # 跳过表头
            
            history = []
            for row in history_rows:
                cols = row.find_all('td')
                history_record = {
                    'date': cols[0].text.strip(),
                    'actual_growth': cols[1].text.strip(),
                    'estimated_growth': cols[2].text.strip()
                }
                history.append(history_record)
            
            # 整合所有数据
            fund_info = {
                'real_time_value': {
                    'real_time': {
                        'value': real_time_value,
                        'change': None,
                        'change_percent': None,
                        'update_time': None
                    },
                    'latest_net': None
                },
                'holdings': holdings,
                'history': history
            }
            
            return fund_info
            
        except Exception as e:
            logging.error(f"解析基金信息失败: {str(e)}")
            return None

    def save_to_csv(self, fund_data, output_dir='output'):
        """
        将基金数据保存为CSV文件
        
        Args:
            fund_data (dict): 基金数据
            output_dir (str): 输出目录
        """
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存重仓股数据
            holdings_df = pd.DataFrame(fund_data['holdings'])
            holdings_df.to_csv(f"{output_dir}/holdings.csv", index=False, encoding='utf-8-sig')
            
            # 保存历史对照数据
            history_df = pd.DataFrame(fund_data['history'])
            history_df.to_csv(f"{output_dir}/history.csv", index=False, encoding='utf-8-sig')
            
            # 保存实时估值
            with open(f"{output_dir}/real_time_value.json", 'w', encoding='utf-8') as f:
                json.dump(fund_data['real_time_value'], f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            logging.error(f"保存数据失败: {str(e)}")
            return False

def main():
    fund_codes = ['017811', '016387']
    query = FundQuery()
    
    for fund_code in fund_codes:
        print(f"\n处理基金 {fund_code}...")
        
        fund_info = query.get_fund_info(fund_code)
        
        if fund_info:
            output_dir = f"output/{fund_code}"
            
            print("\n实时估值信息:")
            rtv = fund_info['real_time_value']['real_time']
            print(f"实时估值: {rtv['value']}")
            print(f"估算涨跌: {rtv['change']} ({rtv['change_percent']})")
            print(f"更新时间: {rtv['update_time']}")
            
            print("\n最新净值信息:")
            net = fund_info['real_time_value']['latest_net']
            print(f"最新净值: {net['value']}")
            print(f"净值日期: {net['date']}")
            print(f"涨跌幅: {net['change']} ({net['change_percent']})")
            
            print("\n重仓股信息:")
            for holding in fund_info['holdings']:
                print(f"{holding['stock_name']}({holding['stock_code']}): "
                      f"持仓{holding['position_ratio']}, "
                      f"涨跌{holding['change_percent']}, "
                      f"贡献{holding['contribution']}")
            
            print("\n历史对照:")
            for record in fund_info['history']:
                print(f"{record['date']}: "
                      f"实际{record['actual_growth']}, "
                      f"预估{record['estimated_growth']}")
            
            # 保存到CSV文件
            query.save_to_csv(fund_info, output_dir)
        else:
            print(f"获取基金 {fund_code} 信息失败")
        
        # 添加适当的延时，避免请求过于频繁
        time.sleep(1)

if __name__ == "__main__":
    main() 