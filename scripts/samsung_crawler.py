# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import logging
import traceback
import random
import datetime
import csv

# 时间戳
ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# 创建Logger对象
logger = logging.getLogger(__name__)

# 设置日志级别
logger.setLevel(logging.DEBUG)

# 创建FileHandler对象
file_handler = logging.FileHandler("{}.log".format(ts))

# 创建StreamHandler对象
stream_handler = logging.StreamHandler()

# 创建Formatter对象
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# 将Formatter对象添加到handler中
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# 将handler添加到logger中
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def html_table_to_dict(html):
    # 创建BeautifulSoup对象
    soup = BeautifulSoup(html, 'html.parser')
    # 找到第一个table元素
    table = soup.find('table')
    # 找到所有的tr元素
    rows = table.find_all('tr')
    # 创建一个空字典，用于存储表格数据
    table_data = {}
    # 遍历每一行，将每个单元格的内容添加到字典中
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 1:
            table_data[cells[0].text] = cells[1].text
    return table_data

def get_model_info(name, url):
    """获取机型详细信息

    Args:
        url (_type_): 机型的完整url
    """
    # logger.info("采集机型信息: {}".format(url))
    response = requests.get(url)
    # 阻塞3~5s，避免被ban了
    time.sleep(random.randint(3,5))
    table = html_table_to_dict(response.content)
    model_info = {"brand":table["Brand"], "name":name, "region":table["Country or region available"], "release":table["Release date"], "chipset":table["Chipset"], "GPU":table["GPU graphical controller"]}
    logger.info(model_info)
    return model_info

with open('samsung_{}.csv'.format(ts), 'a', newline='',encoding='utf-8') as csvfile:
    # 定义CSV文件的列名
    fieldnames = ['brand', 'name', 'region', 'release', 'chipset', 'GPU']

    # 创建一个csv.DictWriter对象
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    base = "https://www.phonemore.com"

    # 从第一页开始采集数据
    page_url = "https://www.phonemore.com/specs/samsung/"
    page = 1

    # 遍历每一页
    while True:
        try:
            logger.info("开始采集第{}页: {}".format(page,page_url))
            response = requests.get(page_url)
            if(response.ok is False):
                logger.error("无法请求：{}, 状态码：{}, 原因：".format(page_url, response.status_code, response.reason))
                break;
            soup = BeautifulSoup(response.content, "html.parser")
            devices = soup.find_all("div", {"class", "itemp"})
            # 获取当前页面中的设备信息
            for device in devices:
                device_name = device.find("strong").text
                logger.info("设备 {} 的型号：".format(device_name))
                # 每个设备可能对应多个不同的版本
                options = device.find_all("option")
                options = options[1:-1] if len(options) > 2 else options[1:]
                for option in options:
                    model_name = option.text[1:-1] # 去除首尾括号
                    model_url = base + option.get("value")
                    logger.info("型号{}: {}".format(model_name, model_url))
                    # 获取机型数据并保存到csv
                    model_info = get_model_info(model_name, model_url)
                    # 写入一行数据
                    writer.writerow(model_info)
                    
            # 下一页
            next_page = soup.find("a", text="Next page")
            if(next_page is None):
                logging.info("无法找到下一页，抓取完毕")
                break
            page_url = base + next_page.get("href")
            page = page + 1
            # 阻塞3~5s，避免被ban了
            time.sleep(random.randint(3,5))
        except Exception as e:
            # 任何异常都会结束采集，比如无法找到下一页的url
            traceback.print_exc()
            break
