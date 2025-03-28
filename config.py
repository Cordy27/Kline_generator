# -*- coding: utf-8 -*-
"""K线图配置文件
包含技术指标显示选项和颜色设置
"""

# 技术指标显示选项
INDICATORS = {
    'MA5': True,      # 5日移动平均线
    'MA20': True,     # 20日移动平均线
    'VWAP': True,     # 成交量加权平均价格
    'RSI': False,      # 相对强弱指标
    'BOLL': False,     # 布林带
    'MACD': True,      # MACD指标
}

# 颜色设置（符合中国市场习惯）
COLORS = {
    # K线颜色
    'up_color': 'red',          # 上涨颜色
    'down_color': 'green',      # 下跌颜色
    
    # 技术指标颜色
    'MA5_color': 'red',         # MA5线颜色
    'MA20_color': 'blue',       # MA20线颜色
    'VWAP_color': 'purple',     # VWAP线颜色
    'RSI_color': 'green',       # RSI线颜色
    
    # 布林带颜色
    'BOLL_up_color': 'gray',    # 布林带上轨颜色
    'BOLL_mid_color': 'gray',   # 布林带中轨颜色
    'BOLL_down_color': 'gray',  # 布林带下轨颜色
    
    # MACD颜色
    'MACD_fast_color': 'blue',   # MACD快线颜色
    'MACD_slow_color': 'orange', # MACD慢线颜色
    'MACD_hist_color': 'red',    # MACD柱状图颜色
}

# 时间跨度设置
TIME_RANGE = {
    'start_date': '20230101',  # 起始日期，格式：YYYYMMDD
    'end_date': None,          # 结束日期，格式：YYYYMMDD，None表示当前日期
    'window_months': 3,        # 时间窗口大小（月数）
}

# 图表风格预设
CHART_STYLES = {
    'default': {
        'style': 'default',     # mplfinance内置风格
        'gridstyle': '--',      # 网格线样式
        'y_on_right': True,     # Y轴显示在右侧
        'figsize': (16, 16),    # 图表大小
        'panel_ratios': (3, 3, 3),  # 面板比例（K线:成交量:MACD）
        'dpi': 300,             # 图像分辨率
        'linewidth': 1.2,       # 线条宽度
        'rc': {'font.size': 12, # 基础字体大小
               'axes.labelsize': 20, # 坐标轴标签大小
               'figure.titlesize': 40},  # 标题字体大小
        'tight_layout': True,   # 紧凑布局
    },
    'dark': {
        'style': 'mike',        # mike是mplfinance支持的深色风格
        'gridstyle': '--',
        'y_on_right': True,
        'figsize': (16, 16),
        'panel_ratios': (3, 3, 3),
        'dpi': 300,
        'linewidth': 1.2,
        'rc': {'font.size': 12,
               'axes.labelsize': 20,
               'figure.titlesize': 40},
        'tight_layout': True,
    },
    'classic': {
        'style': 'classic',     # 经典风格
        'gridstyle': '-',
        'y_on_right': False,    # Y轴显示在左侧
        'figsize': (16, 16),
        'panel_ratios': (3, 3, 3),
        'dpi': 300,
        'linewidth': 1.0,
        'rc': {'font.size': 10,
               'axes.labelsize': 20,
               'figure.titlesize': 40},
        'tight_layout': True,
    },
    'yahoo': {
        'style': 'yahoo',       # 类雅虎财经风格
        'gridstyle': '--',
        'y_on_right': True,
        'figsize': (16, 16),
        'panel_ratios': (3, 3, 3),
        'dpi': 300,
        'linewidth': 1.2,
        'rc': {'font.size': 12,
               'axes.labelsize': 20,
               'figure.titlesize': 40},
        'tight_layout': True,
    },
    # 以下是新增加的样式
    'blueskies': {
        'style': 'blueskies',   # 蓝天风格
        'gridstyle': '--',
        'y_on_right': True,
        'figsize': (16, 16),
        'panel_ratios': (3, 3, 3),
        'dpi': 300,
        'linewidth': 1.2,
        'rc': {'font.size': 12,
               'axes.labelsize': 20,
               'figure.titlesize': 40},
        'tight_layout': True,
    },
    'brasil': {
        'style': 'brasil',      # 巴西风格
        'gridstyle': '--',
        'y_on_right': True,
        'figsize': (16, 16),
        'panel_ratios': (3, 3, 3),
        'dpi': 300,
        'linewidth': 1.2,
        'rc': {'font.size': 12,
               'axes.labelsize': 20,
               'figure.titlesize': 40},
        'tight_layout': True,
    },
    'charles': {
        'style': 'charles',     # charles风格 
        'gridstyle': '--',
        'y_on_right': True,
        'figsize': (16, 16),
        'panel_ratios': (3, 3, 3),
        'dpi': 300,
        'linewidth': 1.2,
        'rc': {'font.size': 12,
               'axes.labelsize': 20,
               'figure.titlesize': 40},
        'tight_layout': True,
    },
    'checkers': {
        'style': 'checkers',    # 棋盘格风格
        'gridstyle': '--',
        'y_on_right': True,
        'figsize': (16, 16),
        'panel_ratios': (3, 3, 3),
        'dpi': 300,
        'linewidth': 1.2,
        'rc': {'font.size': 12,
               'axes.labelsize': 20,
               'figure.titlesize': 40},
        'tight_layout': True,
    },
    'mike': {
        'style': 'mike',        # mike风格
        'gridstyle': '--',
        'y_on_right': True,
        'figsize': (16, 16),
        'panel_ratios': (3, 3, 3),
        'dpi': 300,
        'linewidth': 1.2,
        'rc': {'font.size': 12,
               'axes.labelsize': 20,
               'figure.titlesize': 40},
        'tight_layout': True,
    },
    'nightclouds': {
        'style': 'nightclouds', # 夜云风格
        'gridstyle': '--',
        'y_on_right': True,
        'figsize': (16, 16),
        'panel_ratios': (3, 3, 3),
        'dpi': 300,
        'linewidth': 1.2,
        'rc': {'font.size': 12,
               'axes.labelsize': 20,
               'figure.titlesize': 40},
        'tight_layout': True,
    },
    'sas': {
        'style': 'sas',         # SAS风格
        'gridstyle': '--',
        'y_on_right': True,
        'figsize': (16, 16),
        'panel_ratios': (3, 3, 3),
        'dpi': 300,
        'linewidth': 1.2,
        'rc': {'font.size': 12,
               'axes.labelsize': 20,
               'figure.titlesize': 40},
        'tight_layout': True,
    },
    'starsandstripes': {
        'style': 'starsandstripes', # 星条旗风格
        'gridstyle': '--',
        'y_on_right': True,
        'figsize': (16, 16),
        'panel_ratios': (3, 3, 3),
        'dpi': 300,
        'linewidth': 1.2,
        'rc': {'font.size': 12,
               'axes.labelsize': 20,
               'figure.titlesize': 40},
        'tight_layout': True,
    },
}

# 当前选择的图表风格（默认使用'default'风格）
CURRENT_STYLE = 'default'

# 图表样式设置 (为了向后兼容保留)
STYLE = CHART_STYLES['default']
