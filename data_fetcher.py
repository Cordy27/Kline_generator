# -*- coding: utf-8 -*-
"""获取上证100股票的日线数据
使用tushare API获取数据
"""

import os
import time
import pandas as pd
from dotenv import load_dotenv

# 检查并安装tushare库
try:
    import tushare as ts
except ImportError:
    print("正在安装tushare库...")
    import pip
    pip.main(['install', 'tushare'])
    import tushare as ts

# 检查并安装python-dotenv库
try:
    from dotenv import load_dotenv
except ImportError:
    print("正在安装python-dotenv库...")
    import pip
    pip.main(['install', 'python-dotenv'])
    from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 从环境变量获取token
TOKEN = os.getenv("TUSHARE_TOKEN")

# 检查token是否存在
if not TOKEN:
    print("警告: 未找到TUSHARE_TOKEN环境变量")
    print("请在.env文件中设置TUSHARE_TOKEN=你的token值")
    TOKEN = input("请输入您的tushare token: ").strip()

# 初始化tushare
ts.set_token(TOKEN)
pro = ts.pro_api()

def get_sz100_stocks():
    """
    获取股票列表
    """
    try:
        # 获取上证100成分股
        df = pro.index_weight(index_code='000016.SH', trade_date=time.strftime('%Y%m%d'))
        if df is None or df.empty:
            # 如果当天数据不可用，尝试获取最近的数据
            df = pro.index_weight(index_code='000016.SH')
        
        # 提取股票代码列表
        stocks = list(df['con_code'])
        return stocks
    except Exception as e:
        print(f"\n[ERROR] 获取上证100成分股失败")
        return []

def get_daily_kline(ts_code, start_date='20230101', end_date=None):
    """
    获取指定股票的日线数据
    
    参数:
        ts_code: 股票代码
        start_date: 开始日期，默认为2023年1月1日
        end_date: 结束日期，默认为当前日期
    
    返回:
        DataFrame: 日线数据
    """
    if end_date is None:
        end_date = time.strftime('%Y%m%d')
    
    try:
        # 使用pro_bar接口获取日线数据
        df = ts.pro_bar(ts_code=ts_code, 
                       freq='D',  # 日线频率
                       start_date=start_date, 
                       end_date=end_date,
                       adj='qfq')     # 前复权
        
        # 确保数据按日期排序
        if df is not None and not df.empty:
            df = df.sort_values('trade_date', ascending=True)
        
        return df
    except Exception as e:
        print(f"获取{ts_code}的日线数据失败: {e}")
        return None

def save_data(df, stock_code, folder='daily_data'):
    """
    保存数据到CSV文件
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, "daily.csv")
    df.to_csv(file_path, index=False)
    print(f"数据已保存到 {file_path}")
    return file_path

def main():
    print("开始获取上证100股票的日线数据...")
    
    # 获取上证100成分股
    stocks = get_sz100_stocks()
    if not stocks:
        print("未能获取上证100成分股列表，将使用提供的股票代码")
        try:
            # 检查文件是否存在
            if not os.path.exists('stockcode.csv'):
                raise FileNotFoundError("股票代码文件不存在")
            
            # 读取股票代码文件
            stocks = pd.read_csv('stockcode.csv', dtype={'0': str})
            
            # 检查是否为空DataFrame
            if stocks.empty:
                raise ValueError("股票代码文件为空")
                
            # 如果stocks是DataFrame，获取股票代码列
            if isinstance(stocks, pd.DataFrame):
                # 假设股票代码在第一列
                stocks = stocks.iloc[:, 0].astype(str).tolist()
                
        except Exception as e:
            print(f"读取股票代码文件失败: {e}")
            stocks = []
    
    print(f"共获取到 {len(stocks)} 只股票")
    
    # 创建数据文件夹
    data_folder = 'daily_data'
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    # 获取每只股票的日线数据
    # 询问用户是否限制获取的股票数量
    limit_option = input("是否限制获取的股票数量？(y/n): ").strip().lower()
    
    if limit_option == 'y':
        try:
            limit_count = int(input("请输入要获取的股票数量: "))
            stocks_to_fetch = stocks[:limit_count]
        except ValueError:
            print("输入无效，将获取所有股票数据")
            stocks_to_fetch = stocks
    else:
        stocks_to_fetch = stocks
    
    total_stocks = len(stocks_to_fetch)
    
    for i, stock in enumerate(stocks_to_fetch):
        print(f"正在获取第 {i+1}/{total_stocks} 只股票 {stock} 的数据...")
        
        # 获取日线数据
        df = get_daily_kline(stock)
        
        if df is not None and not df.empty:
            # 保存数据
            save_data(df, stock, data_folder)
            
            # 打印数据概览
            print(f"\n{stock} 数据概览:")
            print(df.head())
        else:
            print(f"未能获取 {stock} 的数据")
        
        # 避免频繁请求导致API限制
        time.sleep(1)
    
    print("\n数据获取完成!")

if __name__ == "__main__":
    main()