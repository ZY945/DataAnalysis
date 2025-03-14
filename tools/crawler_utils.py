import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import logging

class CrawlerUtils:
    @staticmethod
    def get_html_by_requests(url, headers=None, params=None, timeout=10):
        """
        使用requests库获取网页HTML内容
        
        Args:
            url (str): 目标URL
            headers (dict): 请求头
            params (dict): URL参数
            timeout (int): 超时时间（秒）
            
        Returns:
            str: HTML内容
        """
        try:
            if headers is None:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except Exception as e:
            logging.error(f"获取页面失败: {url}, 错误: {str(e)}")
            return None

    @staticmethod
    def post_request(url, data=None, json=None, headers=None, timeout=10):
        """
        发送POST请求
        
        Args:
            url (str): 目标URL
            data (dict): 表单数据
            json (dict): JSON数据
            headers (dict): 请求头
            timeout (int): 超时时间（秒）
            
        Returns:
            str: 响应内容
        """
        try:
            if headers is None:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            
            response = requests.post(url, data=data, json=json, headers=headers, timeout=timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except Exception as e:
            logging.error(f"POST请求失败: {url}, 错误: {str(e)}")
            return None

    @staticmethod
    def get_html_by_selenium(url, wait_time=10, headless=True):
        """
        使用Selenium获取网页HTML内容
        
        Args:
            url (str): 目标URL
            wait_time (int): 等待时间（秒）
            headless (bool): 是否使用无头模式
            
        Returns:
            str: HTML内容
        """
        driver = None
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # 等待页面加载完成
            time.sleep(wait_time)
            
            return driver.page_source
        except Exception as e:
            logging.error(f"Selenium获取页面失败: {url}, 错误: {str(e)}")
            return None
        finally:
            if driver:
                driver.quit()

    @staticmethod
    def wait_for_element_and_get_html(url, by, value, wait_time=10, headless=True):
        """
        使用Selenium等待特定元素出现后获取HTML
        
        Args:
            url (str): 目标URL
            by: 元素定位方式（例如：By.ID, By.CLASS_NAME等）
            value (str): 元素定位值
            wait_time (int): 等待时间（秒）
            headless (bool): 是否使用无头模式
            
        Returns:
            str: HTML内容
        """
        driver = None
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # 等待特定元素出现
            wait = WebDriverWait(driver, wait_time)
            wait.until(EC.presence_of_element_located((by, value)))
            
            return driver.page_source
        except TimeoutException:
            logging.error(f"等待元素超时: {url}, 元素: {value}")
            return None
        except Exception as e:
            logging.error(f"Selenium获取页面失败: {url}, 错误: {str(e)}")
            return None
        finally:
            if driver:
                driver.quit() 