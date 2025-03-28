# -*- coding: utf-8 -*-
"""使用mplfinance绘制专业的K线图
包含开高低收价格和成交量信息
"""

import os
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from ta.trend import sma_indicator, macd
from ta.volume import volume_weighted_average_price
from ta.momentum import rsi
from ta.volatility import BollingerBands
from config import INDICATORS, COLORS, CHART_STYLES, CURRENT_STYLE, TIME_RANGE  # 导入配置参数

# 导入tqdm用于显示进度条
try:
    from tqdm import tqdm
    from tqdm.auto import tqdm as auto_tqdm
except ImportError:
    print("正在安装tqdm库...")
    import pip
    pip.main(['install', 'tqdm'])
    from tqdm import tqdm
    from tqdm.auto import tqdm as auto_tqdm

# 添加信号处理
import signal
import traceback

# 全局变量，用于中断处理
interrupted = False

# 信号处理函数
def signal_handler(sig, frame):
    global interrupted
    print("\n程序接收到中断信号，正在完成当前任务后退出...")
    interrupted = True

# 注册信号处理函数
signal.signal(signal.SIGINT, signal_handler)

# 添加Windows系统字体路径
font_dirs = ['C:/Windows/Fonts']
font_files = fm.findSystemFonts(fontpaths=font_dirs)

# 添加所有系统字体
for font_file in font_files:
    fm.fontManager.addfont(font_file)

# 设置matplotlib中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong']  # 设置多个备选中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def load_data(file_path):
    """加载CSV文件中的股票数据，并根据配置的时间跨度筛选数据"""
    df = pd.read_csv(file_path)
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index('trade_date', inplace=True)
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'vol': 'Volume'
    })
    df = df.sort_index(ascending=True)
    
    # 根据配置的时间跨度筛选数据
    if TIME_RANGE['start_date']:
        start_date = pd.to_datetime(TIME_RANGE['start_date'], format='%Y%m%d')
        df = df[df.index >= start_date]
    if TIME_RANGE['end_date']:
        end_date = pd.to_datetime(TIME_RANGE['end_date'], format='%Y%m%d')
        df = df[df.index <= end_date]
    
    # 按时间窗口分组
    window_months = TIME_RANGE['window_months']
    df['year_month'] = df.index.to_period('M')
    df['window_group'] = (df['year_month'].astype('int64').astype('int32') - df['year_month'].astype('int64').astype('int32').min()) // window_months
    
    return df

def calculate_indicators(df):
    """根据配置计算技术指标"""
    result_df = df.copy()
    
    if INDICATORS['MA5']:
        result_df['MA5'] = sma_indicator(result_df['Close'], window=5)
    if INDICATORS['MA20']:
        result_df['MA20'] = sma_indicator(result_df['Close'], window=20)
    if INDICATORS['VWAP']:
        result_df['VWAP'] = volume_weighted_average_price(
            high=result_df['High'],
            low=result_df['Low'],
            close=result_df['Close'],
            volume=result_df['Volume']
        )
    if INDICATORS['RSI']:
        result_df['RSI'] = rsi(result_df['Close'], window=14)
    if INDICATORS['BOLL']:
        indicator_bb = BollingerBands(close=result_df['Close'], window=20, window_dev=2)
        result_df['BB_H'] = indicator_bb.bollinger_hband()
        result_df['BB_M'] = indicator_bb.bollinger_mavg()
        result_df['BB_L'] = indicator_bb.bollinger_lband()
    
    if INDICATORS['MACD']:
        # 计算MACD指标
        macd_diff = macd(result_df['Close'])
        macd_signal = macd_diff.ewm(span=9, adjust=False).mean()
        macd_hist = macd_diff - macd_signal
        
        # 分别存储MACD的各个组件
        result_df['MACD'] = macd_diff
        result_df['MACD_signal'] = macd_signal
        result_df['MACD_hist'] = macd_hist
        
        # 分别计算正负值的MACD柱状图
        result_df['MACD_hist_pos'] = result_df['MACD_hist'].where(result_df['MACD_hist'] > 0, 0)
        result_df['MACD_hist_neg'] = result_df['MACD_hist'].where(result_df['MACD_hist'] <= 0, 0)
    
    return result_df

def plot_stock_kline(df, stock_code, save_path=None, style_name=None):
    """使用mplfinance绘制专业的K线图
    
    参数:
        df: 数据框，包含股票价格数据
        stock_code: 股票代码
        save_path: 保存路径，若为None则显示图表
        style_name: 图表风格名称，对应config.py中的CHART_STYLES
    """
    # 使用指定的风格或当前默认风格
    if style_name is None:
        style_name = CURRENT_STYLE
    
    # 如果指定的风格不存在，使用默认风格
    if style_name not in CHART_STYLES:
        print(f"警告: 风格 '{style_name}' 不存在，使用默认风格")
        style_name = 'default'
    
    # 获取选择的风格设置
    style_settings = CHART_STYLES[style_name]
    
    # 先计算所有技术指标
    df = calculate_indicators(df)
    
    # 获取时间窗口数量
    num_windows = df['window_group'].nunique()
    
    for window_idx in range(num_windows):
        # 获取当前时间窗口的数据
        window_df = df[df['window_group'] == window_idx].copy()
        window_df = window_df.drop(['year_month', 'window_group'], axis=1)
        
        # 创建附加图表
        apds = []
        if INDICATORS['MA5']:
            apds.append(mpf.make_addplot(window_df['MA5'], color=COLORS['MA5_color'], width=0.7, label='MA5'))
        if INDICATORS['MA20']:
            apds.append(mpf.make_addplot(window_df['MA20'], color=COLORS['MA20_color'], width=0.7, label='MA20'))
        if INDICATORS['VWAP']:
            apds.append(mpf.make_addplot(window_df['VWAP'], color=COLORS['VWAP_color'], width=0.7, label='VWAP'))
        if INDICATORS['BOLL']:
            apds.extend([
                mpf.make_addplot(window_df['BB_H'], color=COLORS['BOLL_up_color'], width=0.7, label='BB上轨'),
                mpf.make_addplot(window_df['BB_M'], color=COLORS['BOLL_mid_color'], width=0.7, label='BB中轨', linestyle='--'),
                mpf.make_addplot(window_df['BB_L'], color=COLORS['BOLL_down_color'], width=0.7, label='BB下轨')
            ])
        if INDICATORS['RSI']:
            apds.append(mpf.make_addplot(window_df['RSI'], panel=2, color=COLORS['RSI_color'], width=0.7, label='RSI'))
        
        if INDICATORS['MACD']:
            # 添加MACD指标到第三个面板，确保所有MACD指标共用同一个Y轴
            apds.extend([
                mpf.make_addplot(window_df['MACD'], panel=2, color=COLORS['MACD_fast_color'], width=0.7, label='MACD', ylabel='MACD'),
                mpf.make_addplot(window_df['MACD_signal'], panel=2, color=COLORS['MACD_slow_color'], width=0.7, label='Signal', secondary_y=False),
                mpf.make_addplot(window_df['MACD_hist_pos'], type='bar', panel=2, color='red', label='MACD Histogram Positive', secondary_y=False),
                mpf.make_addplot(window_df['MACD_hist_neg'], type='bar', panel=2, color='green', label='MACD Histogram Negative', secondary_y=False)
            ])
        
        # 设置K线图样式
        mc = mpf.make_marketcolors(
            up=COLORS['up_color'],
            down=COLORS['down_color'],
            edge='inherit',
            wick='inherit',
            volume='inherit'
        )
        
        # 设置图表风格
        s = mpf.make_mpf_style(
            base_mpf_style=style_settings.get('style', 'default'),  # 使用预设的基础风格
            marketcolors=mc,
            gridstyle=style_settings.get('gridstyle', '--'),
            y_on_right=style_settings.get('y_on_right', True),
            rc=style_settings.get('rc', {'font.size': 12})
        )
        
        # 获取时间窗口的起止日期
        window_start = window_df.index[0].strftime('%Y%m%d')
        window_end = window_df.index[-1].strftime('%Y%m%d')
        
        # 创建图形
        fig, axes = mpf.plot(
            window_df,
            type='candle',
            volume=True,
            addplot=apds,
            title=f'{stock_code} K线图 ({window_start}-{window_end})',
            ylabel='价格',
            ylabel_lower='成交量',
            style=s,
            figsize=style_settings.get('figsize', (16, 16)),
            panel_ratios=style_settings.get('panel_ratios', (6, 2, 2)),
            returnfig=True
        )
        
        # 设置标题和标签的字体
        title = fig.texts[0]
        title.set_fontproperties(fm.FontProperties(fname='C:/Windows/Fonts/simhei.ttf', size=style_settings['rc'].get('figure.titlesize', 16)))
        
        for ax in axes:
            if ax is not None:
                # 设置标题和标签的字体大小
                ax.set_title(ax.get_title(), fontproperties=fm.FontProperties(fname='C:/Windows/Fonts/simhei.ttf', size=style_settings['rc'].get('font.size', 12)))
                ax.set_ylabel(ax.get_ylabel(), fontproperties=fm.FontProperties(fname='C:/Windows/Fonts/simhei.ttf', size=style_settings['rc'].get('axes.labelsize', 14)))
                
                # 设置刻度标签的字体大小
                ax.tick_params(axis='both', labelsize=style_settings['rc'].get('font.size', 12))
                
                # 如果有图例，设置图例的字体大小和字体属性
                if ax.get_legend() is not None:
                    legend = ax.get_legend()
                    for text in legend.get_texts():
                        text.set_font_properties(fm.FontProperties(fname='C:/Windows/Fonts/simhei.ttf', size=style_settings['rc'].get('font.size', 12)))
        
        # 保存或显示图形
        if save_path:
            # 为每个时间窗口创建单独的文件名
            base_name, ext = os.path.splitext(save_path)
            window_save_path = f"{base_name}_{window_start}_{window_end}_{style_name}{ext}"
            
            # 直接使用bbox_inches='tight'替代tight_layout调用
            # 避免tight_layout兼容性警告
            plt.savefig(window_save_path, dpi=style_settings.get('dpi', 300), bbox_inches='tight')
            plt.close()
        else:
            # 显示图表时，如果用户需要紧凑布局，使用一个安全的方法调整布局
            if style_settings.get('tight_layout', False):
                try:
                    # 使用try-except块避免tight_layout警告影响程序运行
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        fig.tight_layout(pad=1.2)  # 增加边距可以减少不兼容问题
                except Exception as e:
                    print(f"应用tight_layout时出错，但不影响图表显示: {str(e)}")
            plt.show()
            plt.close()

def main():
    # 全局中断标志
    global interrupted
    
    try:
        # 数据文件夹路径
        data_folder = 'daily_data'
        
        # 获取文件夹中所有的CSV文件
        if not os.path.exists(data_folder):
            print(f"未找到数据文件夹：{data_folder}")
            return
        
        csv_files = [f for f in os.listdir(data_folder) if f.endswith('_daily.csv')]
        if not csv_files:
            print(f"在{data_folder}文件夹中未找到任何CSV文件")
            return
        
        print(f"找到{len(csv_files)}个CSV文件，开始生成K线图...", flush=True)
        
        # 获取可用的样式列表
        available_styles = list(CHART_STYLES.keys())
        print(f"可用的图表风格: {', '.join(available_styles)}", flush=True)
        
        # 选择一个图表风格（这里使用当前风格，也可以通过命令行参数或用户输入来选择）
        selected_style = CURRENT_STYLE
        print(f"使用图表风格: {selected_style}", flush=True)
        
        # 创建保存K线图的文件夹
        save_folder = 'kline_images'
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
            print(f"创建保存目录: {save_folder}", flush=True)
        
        # 使用简单进度信息替代tqdm进度条
        print(f"开始处理{len(csv_files)}个CSV文件...", flush=True)
        
        for i, csv_file in enumerate(csv_files):
            if interrupted:
                print("用户已中断，停止处理...", flush=True)
                break
                
            # 每处理5个文件或最后一个文件时显示进度
            if i % 5 == 0 or i == len(csv_files) - 1:
                print(f"处理进度: {i+1}/{len(csv_files)} ({(i+1)/len(csv_files)*100:.1f}%)", flush=True)
                
            # 从文件名中提取股票代码
            stock_code = csv_file.replace('_daily.csv', '')
            
            # 构建数据文件路径
            file_path = os.path.join(data_folder, csv_file)
            
            # 加载数据
            df = load_data(file_path)
            
            # 绘制并保存K线图到专属文件夹，使用选择的风格
            save_path = os.path.join(save_folder, f"{stock_code}_kline_pro.png")
            plot_stock_kline(df, stock_code, save_path, style_name=selected_style)
            
            print(f"已生成 {stock_code} 的K线图", flush=True)
        
        print("所有K线图生成完成！", flush=True)
    except KeyboardInterrupt:
        print("\n用户中断了程序执行!", flush=True)
    except Exception as e:
        print(f"程序执行过程中出错: {str(e)}", flush=True)
        traceback.print_exc()

if __name__ == "__main__":
    # 检查并安装mplfinance
    try:
        import mplfinance as mpf
    except ImportError:
        print("正在安装mplfinance库...")
        import pip
        pip.main(['install', 'mplfinance'])
        import mplfinance as mpf
    
    main()