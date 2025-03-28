# -*- coding: utf-8 -*-
"""生成单根或多根蜡烛图的工具
可以用于详细分析单个交易日的情况
"""

import os
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
from config import COLORS, CHART_STYLES, CURRENT_STYLE

# 添加Windows系统字体路径
font_dirs = ['C:/Windows/Fonts']
font_files = fm.findSystemFonts(fontpaths=font_dirs)

# 添加所有系统字体
for font_file in font_files:
    fm.fontManager.addfont(font_file)

# 设置matplotlib中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong']  # 设置多个备选中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 动态检测tqdm
try:
    from tqdm import tqdm
    # 设置tqdm显示选项，确保在控制台正确显示
    from tqdm.auto import tqdm as auto_tqdm  # 自动选择最佳进度条
except ImportError:
    print("正在安装tqdm库...")
    import pip
    pip.main(['install', 'tqdm'])
    from tqdm import tqdm
    from tqdm.auto import tqdm as auto_tqdm

# 导入信号处理
import signal

# 全局变量，处理中断信号
interrupted = False

# 信号处理函数
def signal_handler(sig, frame):
    global interrupted
    print("\n程序接收到中断信号，正在完成当前任务后退出...")
    interrupted = True

# 注册信号处理函数
signal.signal(signal.SIGINT, signal_handler)

def load_specific_data(file_path, date=None, start_date=None, end_date=None, num_candles=None):
    """加载指定日期的数据或者指定数量的蜡烛图数据
    
    参数:
        file_path: CSV文件路径
        date: 特定日期，格式为'YYYYMMDD'，用于加载单根蜡烛图
        start_date: 开始日期，格式为'YYYYMMDD'
        end_date: 结束日期，格式为'YYYYMMDD'
        num_candles: 要显示的蜡烛图数量，从最新的数据开始往前计算
    
    返回:
        处理后的数据框
    """
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
    
    # 筛选特定日期的数据
    if date:
        target_date = pd.to_datetime(date, format='%Y%m%d')
        df = df[df.index == target_date]
        
        # 如果没有找到指定日期的数据
        if df.empty:
            print(f"警告: 未找到日期 {date} 的数据")
            return None
    
    # 筛选日期范围的数据
    elif start_date and end_date:
        start = pd.to_datetime(start_date, format='%Y%m%d')
        end = pd.to_datetime(end_date, format='%Y%m%d')
        df = df[(df.index >= start) & (df.index <= end)]
        
        # 如果日期范围内没有数据
        if df.empty:
            print(f"警告: 在 {start_date} 到 {end_date} 期间没有找到数据")
            return None
    
    # 筛选最近的N根蜡烛
    elif num_candles:
        if num_candles > len(df):
            print(f"警告: 请求的蜡烛数量 ({num_candles}) 超过了可用数据的数量 ({len(df)})")
            num_candles = len(df)
        
        df = df.iloc[-num_candles:]
    
    return df

def plot_single_candle(df, stock_code, save_path=None, style_name=None, show_details=True):
    """绘制单根或多根蜡烛图，不包含标题和成交量
    
    参数:
        df: 数据框，包含股票价格数据
        stock_code: 股票代码
        save_path: 保存路径，若为None则显示图表
        style_name: 图表风格名称
        show_details: 是否显示详细标注信息
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
        base_mpf_style=style_settings.get('style', 'default'),
        marketcolors=mc,
        gridstyle=style_settings.get('gridstyle', '--'),
        y_on_right=style_settings.get('y_on_right', True),
        rc=style_settings.get('rc', {'font.size': 12})
    )
    
    # 构建标题文本（仅用于文件名和打印信息，不显示在图表上）
    if len(df) == 1:
        date_str = df.index[0].strftime('%Y-%m-%d')
        title_text = f'{stock_code} 单日蜡烛图 ({date_str})'
    else:
        start_date = df.index[0].strftime('%Y-%m-%d')
        end_date = df.index[-1].strftime('%Y-%m-%d')
        title_text = f'{stock_code} 蜡烛图 ({start_date} 至 {end_date})'
    
    # 绘制蜡烛图（不包含标题和成交量）
    fig, ax = mpf.plot(
        df,
        type='candle',
        volume=False,  # 不显示成交量
        style=s,
        title='',      # 空标题
        figsize=style_settings.get('figsize', (12, 8)),  # 调整图表比例
        datetime_format='%Y-%m-%d',  # 日期格式
        xrotation=45,  # X轴标签旋转角度
        returnfig=True
    )
    
    # 添加详细信息标注
    if len(df) == 1 and show_details:
        candle_data = df.iloc[0]
        # 获取主K线图的轴对象 (仅有一个轴)
        main_ax = ax[0]
        
        # 添加价格水平线
        main_ax.axhline(y=candle_data['Open'], color='blue', linestyle='--', linewidth=0.8, label='开盘价')
        main_ax.axhline(y=candle_data['Close'], color='red', linestyle='--', linewidth=0.8, label='收盘价')
        main_ax.axhline(y=candle_data['High'], color='green', linestyle='--', linewidth=0.8, label='最高价')
        main_ax.axhline(y=candle_data['Low'], color='purple', linestyle='--', linewidth=0.8, label='最低价')
        
        # 计算振幅
        amplitude = (candle_data['High'] - candle_data['Low']) / candle_data['Low'] * 100
        
        # 添加文本注释（右上角）
        info_text = (
            f"开盘: {candle_data['Open']:.2f}\n"
            f"收盘: {candle_data['Close']:.2f}\n"
            f"最高: {candle_data['High']:.2f}\n"
            f"最低: {candle_data['Low']:.2f}\n"
            f"成交量: {candle_data['Volume']:.0f}\n"
            f"振幅: {amplitude:.2f}%\n"
            f"涨跌幅: {(candle_data['Close']/candle_data['Open']-1)*100:.2f}%"
        )
        
        # 将文本框放在右上角
        bbox_props = dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8, edgecolor="gray")
        text = main_ax.text(
            0.98, 0.98, info_text, 
            transform=main_ax.transAxes, 
            fontsize=12,
            verticalalignment='top', 
            horizontalalignment='right',
            bbox=bbox_props
        )
        
        # 手动设置中文字体
        font_path = 'C:/Windows/Fonts/simhei.ttf'
        chinese_font = fm.FontProperties(fname=font_path)
        text.set_fontproperties(chinese_font)
        
        # 在最高价和最低价处添加标签
        high_anno = main_ax.annotate(
            f"{candle_data['High']:.2f}", 
            xy=(0, candle_data['High']), 
            xytext=(-50, 0),
            textcoords="offset points",
            fontsize=10,
            color='green',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8)
        )
        high_anno.set_fontproperties(chinese_font)
        
        low_anno = main_ax.annotate(
            f"{candle_data['Low']:.2f}", 
            xy=(0, candle_data['Low']), 
            xytext=(-50, 0),
            textcoords="offset points",
            fontsize=10,
            color='purple',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8)
        )
        low_anno.set_fontproperties(chinese_font)
        
        # 设置Y轴刻度标签字体
        for label in main_ax.get_yticklabels():
            label.set_fontproperties(chinese_font)
        
        # 设置X轴刻度标签字体
        for label in main_ax.get_xticklabels():
            label.set_fontproperties(chinese_font)
        
        # 设置图例字体
        if main_ax.get_legend() is not None:
            for text in main_ax.get_legend().get_texts():
                text.set_fontproperties(chinese_font)
    
    # 保存或显示图形
    if save_path:
        # 直接使用bbox_inches='tight'而不是调用tight_layout()
        # 这样可以避免tight_layout兼容性警告
        plt.savefig(save_path, dpi=style_settings.get('dpi', 300), bbox_inches='tight')
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

def main(limit_files=1, style_name=None, periods=None):
    """主函数
    
    参数:
        limit_files: 要处理的文件数量限制
        style_name: 图表风格名称
        periods: 要生成的多日蜡烛图周期列表，如[5, 10, 20]表示生成5日、10日、20日蜡烛图
    """
    # 全局中断标志
    global interrupted
    
    try:
        # 数据文件夹路径
        data_folder = 'daily_data'
        
        # 检查数据文件夹是否存在
        if not os.path.exists(data_folder):
            print(f"未找到数据文件夹：{data_folder}")
            return
        
        # 获取文件夹中所有的CSV文件
        csv_files = [f for f in os.listdir(data_folder) if f.endswith('_daily.csv')]
        if not csv_files:
            print(f"在{data_folder}文件夹中未找到任何CSV文件")
            return
        
        # 创建保存蜡烛图的主文件夹
        save_folder = 'candle_images'
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        
        # 创建多日蜡烛图的主文件夹
        multi_day_folder = 'multi_day_candles'
        if not os.path.exists(multi_day_folder):
            os.makedirs(multi_day_folder)
        
        # 如果没有指定多日周期，设置默认值
        if periods is None:
            periods = [5, 10, 20]  # 默认生成5日、10日和20日蜡烛图
        
        # 打印可用的样式
        available_styles = list(CHART_STYLES.keys())
        print(f"可用的图表风格: {', '.join(available_styles)}")
        
        # 选择一个图表风格
        selected_style = style_name if style_name in CHART_STYLES else CURRENT_STYLE
        print(f"使用图表风格: {selected_style}")
        
        # 限制处理的文件数量
        files_to_process = csv_files[:limit_files]
        
        print(f"将处理前{len(files_to_process)}个文件: {', '.join([f.replace('_daily.csv', '') for f in files_to_process])}")
        print(f"将为每个股票生成单日蜡烛图和{len(periods)}种多日蜡烛图: {periods} 日")
        
        # 使用position参数为进度条设置不同的位置，避免覆盖
        # 第一级进度条 - 处理文件
        for csv_file in auto_tqdm(files_to_process, desc="处理股票文件", unit="个", position=0):
            if interrupted:
                print("用户已中断处理，正在退出...")
                break
                
            # 从文件名中提取股票代码
            stock_code = csv_file.replace('_daily.csv', '')
            file_path = os.path.join(data_folder, csv_file)
            
            print(f"\n正在处理股票 {stock_code} 的蜡烛图...", flush=True)
            
            # 加载完整数据
            df_full = pd.read_csv(file_path)
            df_full['trade_date'] = pd.to_datetime(df_full['trade_date'], format='%Y%m%d')
            df_full.set_index('trade_date', inplace=True)
            df_full = df_full.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'vol': 'Volume'
            })
            df_full = df_full.sort_index(ascending=True)
            
            # 创建股票专属保存文件夹（单日蜡烛图）
            stock_folder = os.path.join(save_folder, stock_code)
            if not os.path.exists(stock_folder):
                os.makedirs(stock_folder)
            
            # 为多日蜡烛图创建股票专属文件夹
            multi_day_stock_folder = os.path.join(multi_day_folder, stock_code)
            if not os.path.exists(multi_day_stock_folder):
                os.makedirs(multi_day_stock_folder)
            
            # 1. 生成单日蜡烛图
            total_days = len(df_full)
            print(f"股票 {stock_code} 共有 {total_days} 个交易日", flush=True)
            
            try:
                # 第二级进度条 - 单日蜡烛图
                # 使用简单的日期计数代替进度条
                print(f"开始生成 {stock_code} 的单日蜡烛图...", flush=True)
                
                for date_idx, date in enumerate(df_full.index):
                    if interrupted:
                        print("用户已中断处理，跳过剩余单日蜡烛图...")
                        break
                    
                    # 每处理10个日期显示一次进度
                    if date_idx % 10 == 0 or date_idx == len(df_full.index) - 1:
                        print(f"处理单日蜡烛图: {date_idx+1}/{len(df_full.index)} ({(date_idx+1)/len(df_full.index)*100:.1f}%)", flush=True)
                    
                    date_str = date.strftime('%Y%m%d')
                    
                    # 提取当天数据
                    df_day = df_full.loc[[date]]
                    
                    # 生成并保存单日蜡烛图
                    save_path = os.path.join(stock_folder, f"{stock_code}_candle_{date_str}.png")
                    plot_single_candle(df_day, stock_code, save_path, style_name=selected_style)
                
                print(f"股票 {stock_code} 的所有单日蜡烛图生成完成！", flush=True)
            except Exception as e:
                print(f"生成单日蜡烛图时出错: {str(e)}")
                traceback.print_exc()
            
            # 2. 生成多日蜡烛图
            if periods and not interrupted:
                try:
                    # 第二级进度条 - 多日周期
                    for period_idx, period in enumerate(periods):
                        if interrupted:
                            print("用户已中断处理，跳过剩余多日蜡烛图...")
                            break
                        
                        print(f"处理 {period}日周期: {period_idx+1}/{len(periods)}", flush=True)
                        
                        # 为每个周期创建子文件夹
                        period_folder = os.path.join(multi_day_stock_folder, f"{period}日")
                        if not os.path.exists(period_folder):
                            os.makedirs(period_folder)
                        
                        # 计算要生成的窗口数量
                        num_windows = max(1, (len(df_full) - period) // period)
                        
                        # 为窗口循环显示进度
                        print(f"开始生成 {period}日窗口，共 {num_windows} 个...", flush=True)
                        for i in range(num_windows):
                            if interrupted:
                                print(f"用户已中断处理，跳过剩余{period}日窗口...")
                                break
                            
                            # 每处理10个窗口显示一次进度
                            if i % 10 == 0 or i == num_windows - 1:
                                print(f"处理 {period}日窗口: {i+1}/{num_windows} ({(i+1)/num_windows*100:.1f}%)", flush=True)
                            
                            start_idx = i * period
                            end_idx = min(start_idx + period, len(df_full))
                            
                            # 获取这个窗口的数据
                            window_data = df_full.iloc[start_idx:end_idx]
                            
                            if len(window_data) < 2:  # 至少需要2个交易日才能绘制多日图
                                continue
                            
                            # 获取窗口起止日期
                            start_date = window_data.index[0].strftime('%Y%m%d')
                            end_date = window_data.index[-1].strftime('%Y%m%d')
                            
                            # 生成并保存多日蜡烛图
                            save_path = os.path.join(period_folder, f"{stock_code}_{period}日_{start_date}_{end_date}.png")
                            plot_single_candle(window_data, stock_code, save_path, style_name=selected_style, show_details=False)
                        
                        print(f"股票 {stock_code} 的 {period}日 蜡烛图生成完成！", flush=True)
                        
                except Exception as e:
                    print(f"生成多日蜡烛图时出错: {str(e)}")
                    traceback.print_exc()
            
            print(f"股票 {stock_code} 的所有蜡烛图生成完成！", flush=True)
        
        print("所有蜡烛图生成完成！", flush=True)
    except KeyboardInterrupt:
        print("\n用户中断了程序执行!")
    except Exception as e:
        print(f"程序执行过程中出错: {str(e)}")
        import traceback
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
    
    import argparse
    import traceback
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='生成K线图')
    parser.add_argument('--limit', type=int, default=1, help='要处理的文件数量限制（默认为1）')
    parser.add_argument('--style', type=str, help='要使用的图表风格')
    parser.add_argument('--periods', type=int, nargs='+', help='多日蜡烛图的周期，如 5 10 20 表示生成5日、10日和20日图')
    parser.add_argument('--no-single', action='store_true', help='不生成单日蜡烛图')
    parser.add_argument('--no-multi', action='store_true', help='不生成多日蜡烛图')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 处理周期参数
    periods = args.periods
    if args.no_multi:
        periods = []
    
    # 调用main函数
    main(args.limit, args.style, periods) 