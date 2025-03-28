# -*- coding: utf-8 -*-
"""
自动使用所有主题生成K线图脚本
可以自动调用plot_kline.py和plot_single_candle.py，使用所有主题并保存到不同的目录
"""

import os
import subprocess
import shutil
import argparse
import traceback
import sys
import signal
from config import CHART_STYLES

# 全局变量，用于中断处理
interrupted = False

# 信号处理函数
def signal_handler(sig, frame):
    global interrupted
    print("\n程序接收到中断信号，正在完成当前任务后退出...")
    interrupted = True

# 注册信号处理函数
signal.signal(signal.SIGINT, signal_handler)

# 动态检测tqdm
try:
    from tqdm import tqdm
    from tqdm.auto import tqdm as auto_tqdm  # 自动选择最佳进度条
except ImportError:
    print("正在安装tqdm库...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'tqdm'], check=True)
    from tqdm import tqdm
    from tqdm.auto import tqdm as auto_tqdm

def clear_directory(directory):
    """清空指定目录中的所有内容"""
    try:
        if os.path.exists(directory):
            print(f"正在清空目录: {directory}")
            # 删除目录及其所有内容
            shutil.rmtree(directory)
            # 重新创建空目录
            os.makedirs(directory)
            print(f"目录已清空并重新创建: {directory}")
        else:
            # 如果目录不存在，创建它
            os.makedirs(directory)
            print(f"目录已创建: {directory}")
    except Exception as e:
        print(f"清空目录 {directory} 时出错: {str(e)}")
        traceback.print_exc()

def main(limit_files=2, generate_kline=True, generate_candle=True, clear_dirs=True, themes=None, periods=None):
    try:
        if themes is None:
            themes = list(CHART_STYLES.keys())
        print(f"发现{len(themes)}个可用主题: {', '.join(themes)}", flush=True)
        
        # 设置默认的多日周期
        if periods is None:
            periods = [5, 10, 20]  # 默认生成5日、10日和20日蜡烛图
        print(f"将生成多日蜡烛图周期: {periods}日", flush=True)

        # 主目录
        base_kline_dir = 'all_themes_kline'
        base_candle_dir = 'all_themes_candle'
        base_multi_day_dir = 'all_themes_multi_day'
        
        # 清空或创建主目录
        if generate_kline:
            if clear_dirs:
                clear_directory(base_kline_dir)
            elif not os.path.exists(base_kline_dir):
                os.makedirs(base_kline_dir)
                print(f"目录已创建: {base_kline_dir}", flush=True)
        
        if generate_candle:
            if clear_dirs:
                clear_directory(base_candle_dir)
            elif not os.path.exists(base_candle_dir):
                os.makedirs(base_candle_dir)
                print(f"目录已创建: {base_candle_dir}", flush=True)
                
            # 多日蜡烛图目录
            if clear_dirs:
                clear_directory(base_multi_day_dir)
            elif not os.path.exists(base_multi_day_dir):
                os.makedirs(base_multi_day_dir)
                print(f"目录已创建: {base_multi_day_dir}", flush=True)
        
        # 清空中间目录
        if generate_kline and clear_dirs:
            clear_directory('kline_images')
        if generate_candle and clear_dirs:
            clear_directory('candle_images')
            clear_directory('multi_day_candles')
        
        print(f"将为每个主题处理前{limit_files}个股票文件", flush=True)
        if generate_kline:
            print("将生成K线图 (plot_kline.py)", flush=True)
        if generate_candle:
            print("将生成蜡烛图 (plot_single_candle.py)", flush=True)
        
        # 为每个主题生成图表，不使用tqdm，避免嵌套进度条问题
        for i, theme in enumerate(themes):
            # 显示处理进度
            print(f"\n处理主题 [{i+1}/{len(themes)}]: {theme}", flush=True)
            
            # 检查是否被中断
            if interrupted:
                print("用户已中断，结束处理...", flush=True)
                break
            
            print(f"\n{'='*60}", flush=True)
            print(f"正在使用主题 {theme} 生成图表...", flush=True)
            print(f"{'='*60}", flush=True)
            
            try:
                # 1. 修改配置文件中的主题
                update_config_theme(theme)
                
                # 2. 运行plot_kline.py脚本
                if generate_kline:
                    try:
                        print(f"\n>>> 运行 plot_kline.py 使用主题 {theme}...", flush=True)
                        
                        # 不捕获输出，让子进程直接在控制台显示进度条
                        subprocess.run(['python', 'plot_kline.py'], check=True)
                        
                        # 创建主题专用目录并复制文件
                        theme_kline_dir = os.path.join(base_kline_dir, theme)
                        if not os.path.exists(theme_kline_dir):
                            os.makedirs(theme_kline_dir)
                        
                        # 复制生成的图表到主题专用目录
                        copy_images('kline_images', theme_kline_dir)
                    except subprocess.CalledProcessError as e:
                        print(f"运行 plot_kline.py 时出错: 退出代码 {e.returncode}", flush=True)
                    except Exception as e:
                        print(f"生成K线图时出错: {str(e)}", flush=True)
                        traceback.print_exc()
                
                # 3. 运行plot_single_candle.py脚本
                if generate_candle:
                    try:
                        # 构建命令行参数
                        cmd = ['python', 'plot_single_candle.py', '--limit', str(limit_files)]
                        
                        # 添加多日周期参数
                        if periods:
                            cmd.append('--periods')
                            cmd.extend([str(p) for p in periods])
                            
                        print(f"\n>>> 运行 plot_single_candle.py 使用主题 {theme}...", flush=True)
                        print(f">>> 命令: {' '.join(cmd)}", flush=True)
                        
                        # 不捕获输出，让子进程直接在控制台显示进度条
                        subprocess.run(cmd, check=True)
                        
                        # 1. 处理单日蜡烛图
                        # 创建主题专用目录并复制文件
                        theme_candle_dir = os.path.join(base_candle_dir, theme)
                        if not os.path.exists(theme_candle_dir):
                            os.makedirs(theme_candle_dir)
                        
                        # 复制生成的图表到主题专用目录
                        copy_directories('candle_images', theme_candle_dir)
                        
                        # 2. 处理多日蜡烛图
                        theme_multi_day_dir = os.path.join(base_multi_day_dir, theme)
                        if not os.path.exists(theme_multi_day_dir):
                            os.makedirs(theme_multi_day_dir)
                            
                        # 复制多日蜡烛图到主题专用目录
                        copy_directories('multi_day_candles', theme_multi_day_dir)
                    except subprocess.CalledProcessError as e:
                        print(f"运行 plot_single_candle.py 时出错: 退出代码 {e.returncode}", flush=True)
                    except Exception as e:
                        print(f"生成蜡烛图时出错: {str(e)}", flush=True)
                        traceback.print_exc()
            except Exception as e:
                print(f"处理主题 {theme} 时出错: {str(e)}", flush=True)
                traceback.print_exc()
                continue
        
        print("\n所有主题的图表生成完成！", flush=True)
    except KeyboardInterrupt:
        print("\n用户中断了程序执行!", flush=True)
    except Exception as e:
        print(f"脚本执行过程中出错: {str(e)}", flush=True)
        traceback.print_exc()

def update_config_theme(theme_name):
    """更新config.py文件中的当前主题"""
    try:
        with open('config.py', 'r', encoding='utf-8') as f:
            config_content = f.readlines()
        
        # 更新CURRENT_STYLE和STYLE行
        for i, line in enumerate(config_content):
            if line.strip().startswith('CURRENT_STYLE ='):
                config_content[i] = f"CURRENT_STYLE = '{theme_name}'\n"
            elif line.strip().startswith('STYLE ='):
                config_content[i] = f"STYLE = CHART_STYLES['{theme_name}']\n"
        
        # 写回文件
        with open('config.py', 'w', encoding='utf-8') as f:
            f.writelines(config_content)
        
        print(f"已将配置文件中的主题更新为: {theme_name}", flush=True)
    except Exception as e:
        print(f"更新配置文件主题时出错: {str(e)}", flush=True)
        traceback.print_exc()
        raise

def copy_images(source_dir, target_dir):
    """复制源目录中的所有图片到目标目录"""
    try:
        if not os.path.exists(source_dir):
            print(f"警告: 源目录 {source_dir} 不存在", flush=True)
            return
        
        # 获取所有PNG文件
        png_files = [f for f in os.listdir(source_dir) if f.endswith('.png')]
        
        if not png_files:
            print(f"警告: 在 {source_dir} 中没有找到PNG文件", flush=True)
            return
        
        print(f"找到 {len(png_files)} 个PNG文件需要复制...", flush=True)
        
        # 不使用进度条，直接复制文件
        for i, file in enumerate(png_files):
            # 定期显示进度
            if i % 10 == 0 or i == len(png_files) - 1:
                print(f"正在复制: {i+1}/{len(png_files)} ({(i+1)/len(png_files)*100:.1f}%)", flush=True)
                
            source_file = os.path.join(source_dir, file)
            target_file = os.path.join(target_dir, file)
            shutil.copy2(source_file, target_file)
        
        print(f"已将 {source_dir} 中的 {len(png_files)} 张图片复制到 {target_dir}", flush=True)
    except Exception as e:
        print(f"复制图像文件时出错: {str(e)}", flush=True)
        traceback.print_exc()

def copy_directories(source_dir, target_dir):
    """复制源目录及其子目录的结构和内容到目标目录"""
    try:
        if not os.path.exists(source_dir):
            print(f"警告: 源目录 {source_dir} 不存在", flush=True)
            return
        
        # 打印目录内容简略信息
        print(f"处理源目录: {source_dir}", flush=True)
        
        # 获取所有待复制的文件列表
        file_list = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.png'):
                    file_list.append((root, file))
        
        if not file_list:
            print(f"警告: 在 {source_dir} 及其子目录中没有找到PNG文件", flush=True)
            return
        
        print(f"找到 {len(file_list)} 个PNG文件需要复制...", flush=True)
        
        # 不使用进度条，直接复制文件
        for i, (root, file) in enumerate(file_list):
            # 定期显示进度
            if i % 10 == 0 or i == len(file_list) - 1:
                print(f"正在复制: {i+1}/{len(file_list)} ({(i+1)/len(file_list)*100:.1f}%)", flush=True)
                
            # 计算相对路径
            rel_path = os.path.relpath(root, source_dir)
            if rel_path == '.':
                rel_path = ''
            
            # 创建对应的目标目录
            target_path = os.path.join(target_dir, rel_path)
            if not os.path.exists(target_path):
                os.makedirs(target_path)
            
            # 复制文件
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_path, file)
            shutil.copy2(source_file, target_file)
        
        print(f"已将 {source_dir} 及其子目录中的 {len(file_list)} 张图片复制到 {target_dir}", flush=True)
    except Exception as e:
        print(f"复制目录结构时出错: {str(e)}", flush=True)
        traceback.print_exc()

if __name__ == "__main__":
    try:
        # 创建命令行参数解析器
        parser = argparse.ArgumentParser(description='使用所有主题生成K线图')
        parser.add_argument('--limit', type=int, default=2, help='要处理的股票文件数量限制（默认为2）')
        parser.add_argument('--kline-only', action='store_true', help='只生成K线图 (plot_kline.py)')
        parser.add_argument('--candle-only', action='store_true', help='只生成蜡烛图 (plot_single_candle.py)')
        parser.add_argument('--no-clear', action='store_true', help='不清空目标文件夹')
        parser.add_argument('--theme', type=str, help='只处理指定的主题，例如 default, dark, classic 等')
        parser.add_argument('--periods', type=int, nargs='+', help='多日蜡烛图的周期，如 5 10 20 表示生成5日、10日和20日图')
        parser.add_argument('--no-single', action='store_true', help='不生成单日蜡烛图')
        parser.add_argument('--no-multi', action='store_true', help='不生成多日蜡烛图')
        
        # 解析命令行参数
        args = parser.parse_args()
        
        # 处理生成类型
        generate_kline = True
        generate_candle = True
        
        if args.kline_only:
            generate_candle = False
        elif args.candle_only:
            generate_kline = False
        
        # 处理周期参数
        periods = args.periods
        if args.no_multi:
            periods = []
            
        # 获取所有可用的主题
        all_themes = list(CHART_STYLES.keys())
        print(f"发现{len(all_themes)}个可用主题: {', '.join(all_themes)}")
        
        # 如果指定了特定主题，则只处理该主题
        if args.theme:
            if args.theme in all_themes:
                all_themes = [args.theme]
                print(f"将只处理主题: {args.theme}")
            else:
                print(f"警告: 指定的主题 '{args.theme}' 不存在，将处理所有主题")
        
        # 调用main函数
        main(args.limit, generate_kline, generate_candle, not args.no_clear, all_themes, periods)
    except Exception as e:
        print(f"脚本执行过程中出错: {str(e)}")
        traceback.print_exc() 