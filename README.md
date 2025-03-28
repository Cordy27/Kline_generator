# K线图生成工具

## 项目概述

本项目是一个K线图生成工具，用于自动化生成股票K线图、蜡烛图和多日周期图表。支持多种可视化主题，可以生成专业的技术分析图表，适用于股票数据分析和可视化。

## 功能特性

- 生成专业K线图，包含多种技术指标（MA5, MA20, VWAP, RSI, BOLL, MACD等）
- 生成单日蜡烛图，显示详细价格信息
- 生成多日周期蜡烛图（如5日、10日、20日）
- 支持多种可视化主题（default, dark, classic, yahoo等）
- 支持批量处理多只股票数据
- 提供命令行参数，灵活配置生成选项
- 自动化处理并保存到相应目录

## 安装说明

### 依赖环境

- Python 3.6+
- 依赖库：pandas, numpy, matplotlib, mplfinance, tqdm, ta, python-dotenv

### 安装步骤

1. 克隆仓库到本地
```
git clone https://github.com/Cordy27/Kline_generator.git
cd Kline_generator
```

2. 安装依赖库
```
pip install pandas numpy matplotlib mplfinance tqdm ta python-dotenv
```

3. 配置Tushare Token
```
cp .env.example .env
```
然后编辑.env文件，将`your_token_here`替换为您的Tushare API token

## 使用方法

### 数据准备

1. 复制`stockcode.csv.example`文件到项目根目录，并重命名为`stockcode.csv`, 并选择需要的股票代码
2. 确保已在`.env`文件中正确配置了Tushare API token
3. 运行```python data_fetcher.py```下载股票数据

### 基本命令

#### 生成K线图

```
python plot_kline.py
```

#### 生成蜡烛图（单日和多日）

```
python plot_single_candle.py --limit 2 --periods 5 10 20
```
参数说明：
- `--limit`: 处理的股票数量
- `--periods`: 多日蜡烛图的周期（天数）

#### 使用所有主题生成图表

```
python auto_generate_all_themes.py --limit 2 --periods 5 10
```
参数说明：
- `--limit`: 处理的股票数量
- `--kline-only`: 只生成K线图
- `--candle-only`: 只生成蜡烛图
- `--no-clear`: 不清空目标文件夹
- `--theme`: 指定单个主题
- `--periods`: 多日蜡烛图的周期
- `--no-single`: 不生成单日蜡烛图
- `--no-multi`: 不生成多日蜡烛图

### 配置说明

在`config.py`中可以配置：
- 技术指标显示选项
- 颜色设置
- 时间跨度设置
- 图表风格预设

在`.env`文件中可以配置：
- Tushare API token (用于获取股票数据)

## 文件结构

- `plot_kline.py`: 生成含技术指标的专业K线图
- `plot_single_candle.py`: 生成单日和多日蜡烛图
- `auto_generate_all_themes.py`: 使用多种主题自动生成图表
- `config.py`: 配置文件，包含风格和指标设置
- `data_fetcher.py`: 数据获取脚本，从Tushare下载股票数据
- `.env.example`: 环境变量配置模板
- `.env`: 包含Tushare API token的环境变量文件(需自行创建)
- `sz100_daily_data/`: 股票数据存放目录
- `kline_images/`: K线图输出目录
- `candle_images/`: 单日蜡烛图输出目录
- `multi_day_candles/`: 多日蜡烛图输出目录
- `all_themes_kline/`: 所有主题K线图存储目录
- `all_themes_candle/`: 所有主题单日蜡烛图存储目录
- `all_themes_multi_day/`: 所有主题多日蜡烛图存储目录

## 使用示例

### 示例1：生成单支股票的K线图

```
python plot_kline.py
```

### 示例2：生成指定数量股票的5日和10日周期图

```
python plot_single_candle.py --limit 1 --periods 5 10
```

### 示例3：使用特定主题生成所有图表

```
python auto_generate_all_themes.py --theme default --limit 1
```

### 示例4：只生成多日蜡烛图，不生成单日图

```
python auto_generate_all_themes.py --candle-only --no-single --limit 1 --periods 5 10
```

## 输出说明

- 单日K线图保存在：`kline_images/`
- 单日蜡烛图保存在：`candle_images/[股票代码]/`
- 多日蜡烛图保存在：`multi_day_candles/[股票代码]/[周期]日/`
- 各主题图表分别保存在对应的`all_themes_`开头的目录中 