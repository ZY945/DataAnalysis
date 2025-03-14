import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import os

class FundQuery:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = "https://www.dayfund.cn/fundpre/{}.html"

    def get_fund_data(self, fund_code):
        try:
            url = self.base_url.format(fund_code)
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return {"error": "请求失败"}

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取基金基本信息
            basic_info = {
                "fund_code": fund_code,
                "fund_name": self._get_fund_name(soup),
                "current_value": self._get_current_value(soup),
                "change_percent": self._get_change_percent(soup),
                "update_time": self._get_update_time(soup),
            }

            # 获取基金持仓信息
            holdings = self._get_holdings(soup)
            
            # 获取历史净值数据
            history = self._get_history_data(soup)

            return {
                "basic_info": basic_info,
                "holdings": holdings,
                "history": history
            }

        except Exception as e:
            return {"error": str(e)}

    def _get_fund_name(self, soup):
        try:
            # 根据实际HTML结构获取基金名称
            name_element = soup.find('h1')
            return name_element.text.strip() if name_element else ""
        except:
            return ""

    def _get_current_value(self, soup):
        try:
            # 获取当前净值
            value_element = soup.find('div', class_='净值')
            return float(value_element.text.strip()) if value_element else 0.0
        except:
            return 0.0

    def _get_change_percent(self, soup):
        try:
            # 获取涨跌幅
            change_element = soup.find('div', class_='涨跌幅')
            return float(change_element.text.strip('%')) if change_element else 0.0
        except:
            return 0.0

    def _get_update_time(self, soup):
        try:
            # 获取更新时间
            time_element = soup.find('div', class_='更新时间')
            return time_element.text.strip() if time_element else ""
        except:
            return ""

    def _get_holdings(self, soup):
        try:
            # 获取持仓信息
            holdings_table = soup.find('table', class_='持仓表')
            if not holdings_table:
                return []

            holdings = []
            rows = holdings_table.find_all('tr')[1:]  # 跳过表头
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    holding = {
                        "stock_code": cols[0].text.strip(),
                        "stock_name": cols[1].text.strip(),
                        "holding_amount": cols[2].text.strip(),
                        "holding_percent": cols[3].text.strip(),
                        "change_percent": cols[4].text.strip()
                    }
                    holdings.append(holding)
            return holdings
        except:
            return []

    def _get_history_data(self, soup):
        try:
            # 获取历史净值数据
            history_table = soup.find('table', class_='历史净值')
            if not history_table:
                return []

            history = []
            rows = history_table.find_all('tr')[1:]  # 跳过表头
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    data = {
                        "date": cols[0].text.strip(),
                        "net_value": cols[1].text.strip(),
                        "change_percent": cols[2].text.strip()
                    }
                    history.append(data)
            return history
        except:
            return []

    def save_to_csv(self, fund_data, output_path):
        """
        将基金数据保存为CSV文件
        """
        try:
            # 保存基本信息
            basic_df = pd.DataFrame([fund_data["basic_info"]])
            basic_df.to_csv(f"{output_path}/basic_info.csv", index=False, encoding='utf-8-sig')

            # 保存持仓信息
            holdings_df = pd.DataFrame(fund_data["holdings"])
            holdings_df.to_csv(f"{output_path}/holdings.csv", index=False, encoding='utf-8-sig')

            # 保存历史数据
            history_df = pd.DataFrame(fund_data["history"])
            history_df.to_csv(f"{output_path}/history.csv", index=False, encoding='utf-8-sig')

            return True
        except Exception as e:
            print(f"保存数据失败: {str(e)}")
            return False

def download_html():
    url = "https://www.dayfund.cn/fundpre/017811.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 创建tools目录下的html文件夹
        save_dir = os.path.join(os.path.dirname(__file__), 'html')
        os.makedirs(save_dir, exist_ok=True)
        
        # 发送请求获取页面内容
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            # 保存HTML文件
            file_path = os.path.join(save_dir, 'fund_017811.html')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"HTML已保存到: {file_path}")
            
            # 打印一些页面内容以供验证
            soup = BeautifulSoup(response.text, 'html.parser')
            print("\n页面标题:", soup.title.string if soup.title else "无标题")
            
        else:
            print(f"下载失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"发生错误: {str(e)}")

# # 使用示例
# if __name__ == "__main__":
#     fund_query = FundQuery()
    
#     # 获取基金数据
#     fund_data = fund_query.get_fund_data("017811")
    
#     # 打印基金数据
#     print(json.dumps(fund_data, ensure_ascii=False, indent=2))
    
#     # 保存到CSV文件
#     fund_query.save_to_csv(fund_data, "./output")
    
#     download_html() 