"""
期货一分钟K线行情分析程序
功能：
1. K线性质识别（大阳、大阴、上影线、下影线、十字星等）
2. K线关系识别（递进、孕中、反走、包含等）
3. K线组合分析（5-12根相连K线）
4. 模拟交易统计（多空仓盈利分析）
5. 生成分析报告
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from collections import defaultdict

# ==================== K线性质识别 ====================

def identify_kline_type(row):
    """
    识别单根K线的性质
    返回: K线类型
    """
    o, h, l, c = row['open'], row['high'], row['low'], row['close']
    
    body = abs(c - o)  # 实体
    upper_shadow = h - max(o, c)  # 上影线
    lower_shadow = min(o, c) - l  # 下影线
    total_range = h - l  # 整体Range
    
    if total_range == 0:
        return "一字板"
    
    body_ratio = body / total_range  # 实体占比
    upper_ratio = upper_shadow / total_range  # 上影占比
    lower_ratio = lower_shadow / total_range  # 下影占比
    
    # 判断涨跌
    is_up = c > o
    is_down = c < o
    is_doji = abs(c - o) / total_range < 0.1  # 十字星阈值
    
    # 大阳线: 实体>60% 且涨幅>1%
    if is_up and body_ratio > 0.6 and (c - o) / o > 0.01:
        if upper_ratio < 0.1 and lower_ratio < 0.1:
            return "大阳线"
        elif upper_ratio > 0.3:
            return "大阳上影"
        elif lower_ratio > 0.3:
            return "大阳下影"
        return "中阳线"
    
    # 大阴线: 实体>60% 且跌幅>1%
    if is_down and body_ratio > 0.6 and (o - c) / o > 0.01:
        if upper_ratio < 0.1 and lower_ratio < 0.1:
            return "大阴线"
        elif upper_ratio > 0.3:
            return "大阴上影"
        elif lower_ratio > 0.3:
            return "大阴下影"
        return "中阴线"
    
    # 十字星类
    if is_doji:
        if upper_ratio > 0.3 and lower_ratio > 0.3:
            return "十字星"
        elif upper_ratio > 0.3:
            return "倒T字"
        elif lower_ratio > 0.3:
            return "T字"
        return "小十字"
    
    # 带长上影
    if upper_ratio > 0.5:
        return "长上影" if is_up else "长上影阴"
    
    # 带长下影
    if lower_ratio > 0.5:
        return "长下影" if is_up else "长下影阴"
    
    # 普通小K线
    if is_up:
        return "小阳线"
    elif is_down:
        return "小阴线"
    else:
        return "小K线"


def identify_kline_relation(prev_row, curr_row):
    """
    识别当前K线与前一根K线的关系
    返回: 关系类型
    """
    if prev_row is None:
        return "首K"
    
    prev_o, prev_c = prev_row['open'], prev_row['close']
    curr_o, curr_c = curr_row['open'], curr_row['close']
    
    prev_body_top = max(prev_o, prev_c)
    prev_body_bottom = min(prev_o, prev_c)
    curr_body_top = max(curr_o, curr_c)
    curr_body_bottom = min(curr_o, curr_c)
    
    prev_mid = (prev_o + prev_c) / 2
    curr_mid = (curr_o + curr_c) / 2
    
    # 包含关系 (prev包含curr 或 curr包含prev)
    if curr_body_top <= prev_body_top and curr_body_bottom >= prev_body_bottom:
        return "被包含"  # curr被prev包含
    if curr_body_top >= prev_body_top and curr_body_bottom <= prev_body_bottom:
        return "包含"  # curr包含prev
    
    # 递进关系 (顺势突破)
    if prev_c > prev_o and curr_o > prev_body_top and curr_c > curr_o:
        return "上涨递进"
    if prev_c < prev_o and curr_o < prev_body_bottom and curr_c < curr_o:
        return "下跌递进"
    
    # 孕中关系 (K线实体在前后K线实体之间)
    if curr_body_top < prev_body_top and curr_body_bottom > prev_body_bottom:
        return "孕中"
    
    # 反走关系 (逆势突破)
    if prev_c > prev_o:  # 上涨趋势中
        if curr_o < prev_body_bottom:  # 低开低走
            return "反走下跌"
    if prev_c < prev_o:  # 下跌趋势中
        if curr_o > prev_body_top:  # 高开高走
            return "反走上涨"
    
    # 盘整关系
    if abs(curr_mid - prev_mid) / prev_mid < 0.002:
        return "横盘"
    
    # 普通关系
    if curr_c > prev_c:
        return "上涨"
    else:
        return "下跌"


def add_technical_indicators(df):
    """
    添加技术指标标识
    """
    df = df.copy()
    
    # 涨跌幅
    df['change_pct'] = (df['close'] - df['open']) / df['open'] * 100
    
    # 成交量变化
    df['volume_change'] = df['volume'].pct_change()
    
    # 持仓变化
    if 'hold' in df.columns:
        df['hold_change'] = df['hold'].pct_change()
    
    # 均线位置 (简单5日均线)
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['close_above_ma5'] = df['close'] > df['ma5']
    
    # 波动率 (5根K线的波动范围)
    df['volatility_5'] = df['high'].rolling(5).max() - df['low'].rolling(5).min()
    df['volatility_ratio'] = df['high'] - df['low']
    
    # 突破标识
    df['high_突破'] = df['high'] > df['high'].shift(1)
    df['low_跌破'] = df['low'] < df['low'].shift(1)
    
    # 成交量放大/缩小
    df['volume放大'] = df['volume'] > df['volume'].shift(1) * 1.5
    df['volume缩小'] = df['volume'] < df['volume'].shift(1) * 0.5
    
    return df


def analyze_kline(df):
    """
    全面分析K线数据
    """
    df = df.copy()
    
    # 添加K线性质
    df['K线性质'] = df.apply(identify_kline_type, axis=1)
    
    # 添加K线关系
    df['K线关系'] = df.apply(
        lambda x: identify_kline_relation(
            df.shift(1).iloc[x.name] if x.name > 0 else None, 
            x
        ), 
        axis=1
    )
    
    # 添加技术指标
    df = add_technical_indicators(df)
    
    return df


# ==================== K线组合分析 ====================

def generate_combinations(df, min_len=5, max_len=12):
    """
    生成所有指定长度的连续K线组合
    """
    combinations = []
    n = len(df)
    
    for length in range(min_len, max_len + 1):
        for i in range(n - length + 1):
            combo = df.iloc[i:i+length].copy()
            combo_reset = combo.reset_index(drop=True)
            combinations.append({
                'length': length,
                'start_idx': i,
                'end_idx': i + length - 1,
                'data': combo_reset,
                'start_time': combo.iloc[0]['datetime'],
                'end_time': combo.iloc[-1]['datetime']
            })
    
    return combinations


def simulate_trade(combo, open_pos_type):
    """
    模拟交易
    open_pos_type: 'long' 或 'short'
    返回: (盈亏金额, 收益率)
    """
    if len(combo) < 2:
        return 0, 0
    
    first_open = combo.iloc[0]['open']
    last_close = combo.iloc[-1]['close']
    
    if open_pos_type == 'long':
        pnl = last_close - first_open
        pnl_pct = (last_close - first_open) / first_open * 100
    else:  # short
        pnl = first_open - last_close
        pnl_pct = (first_open - last_close) / first_open * 100
    
    return pnl, pnl_pct


def get_combo_type(combo):
    """
    获取组合的类型特征 (用于归类)
    """
    if len(combo) < 2:
        return "invalid"
    
    # 统计各类K线数量
    kline_types = combo['K线性质'].tolist()
    
    # 趋势判断
    first_close = combo.iloc[0]['close']
    last_close = combo.iloc[-1]['close']
    
    if last_close > first_close * 1.02:
        trend = "上涨"
    elif last_close < first_close * 0.98:
        trend = "下跌"
    else:
        trend = "震荡"
    
    # 主要K线类型
    main_types = defaultdict(int)
    for kt in kline_types:
        if '阳' in kt:
            main_types['阳线'] += 1
        elif '阴' in kt:
            main_types['阴线'] += 1
        elif '十' in kt or 'T' in kt:
            main_types['星线'] += 1
    
    dominant = max(main_types, key=main_types.get) if main_types else "其他"
    
    # 组合长度
    length = len(combo)
    
    return f"{trend}_{dominant}_{length}K"


def analyze_combinations(df, min_len=5, max_len=12):
    """
    分析所有K线组合
    """
    print(f"正在生成 {min_len}-{max_len} 根K线的所有组合...")
    combinations = generate_combinations(df, min_len, max_len)
    print(f"共生成 {len(combinations)} 个组合")
    
    # 存储结果
    results = []
    
    for i, combo_info in enumerate(combinations):
        if (i + 1) % 5000 == 0:
            print(f"  已处理 {i+1}/{len(combinations)}...")
        
        combo = combo_info['data']
        
        # 获取组合类型
        combo_type = get_combo_type(combo)
        
        # 多仓模拟
        long_pnl, long_pnl_pct = simulate_trade(combo, 'long')
        
        # 空仓模拟
        short_pnl, short_pnl_pct = simulate_trade(combo, 'short')
        
        results.append({
            'combo_type': combo_type,
            'length': combo_info['length'],
            'start_time': combo_info['start_time'],
            'end_time': combo_info['end_time'],
            'long_pnl': long_pnl,
            'long_pnl_pct': long_pnl_pct,
            'long_win': long_pnl > 0,
            'short_pnl': short_pnl,
            'short_pnl_pct': short_pnl_pct,
            'short_win': short_pnl > 0,
        })
    
    return pd.DataFrame(results)


def summarize_results(results_df):
    """
    汇总统计相同类型组合的结果
    """
    if results_df.empty:
        return pd.DataFrame()
    
    summary = results_df.groupby('combo_type').agg({
        'length': ['count', 'mean'],
        'long_pnl_pct': ['mean', 'std', 'min', 'max'],
        'long_win': ['sum', 'mean'],
        'short_pnl_pct': ['mean', 'std', 'min', 'max'],
        'short_win': ['sum', 'mean'],
    }).round(4)
    
    # 扁平化列名
    summary.columns = [
        '组合数量', '平均长度',
        '多仓平均收益%', '多仓收益标准差', '多仓最小收益%', '多仓最大收益%',
        '多仓盈利单数', '多仓胜率',
        '空仓平均收益%', '空仓收益标准差', '空仓最小收益%', '空仓最大收益%',
        '空仓盈利单数', '空仓胜率',
    ]
    
    summary = summary.reset_index()
    summary = summary.sort_values('组合数量', ascending=False)
    
    return summary


def generate_report(df, results_df, summary_df, output_path):
    """
    生成分析报告
    """
    report = []
    report.append("=" * 80)
    report.append("                     期货一分钟K线分析报告")
    report.append("=" * 80)
    report.append("")
    
    # 基本信息
    report.append("【数据概况】")
    report.append(f"  数据时间范围: {df['datetime'].min()} ~ {df['datetime'].max()}")
    report.append(f"  总K线数量: {len(df)}")
    report.append(f"  交易日期: {df['datetime'].dt.date.nunique()} 天")
    report.append("")
    
    # K线性质分布
    report.append("【K线性质分布】")
    type_counts = df['K线性质'].value_counts()
    for ktype, count in type_counts.items():
        pct = count / len(df) * 100
        report.append(f"  {ktype}: {count} ({pct:.1f}%)")
    report.append("")
    
    # K线关系分布
    report.append("【K线关系分布】")
    rel_counts = df['K线关系'].value_counts()
    for rel, count in rel_counts.items():
        pct = count / len(df) * 100
        report.append(f"  {rel}: {count} ({pct:.1f}%)")
    report.append("")
    
    # 组合分析结果
    report.append("【K线组合交易统计】")
    report.append(f"  分析组合数量: {len(results_df)}")
    report.append(f"  组合类型数量: {results_df['combo_type'].nunique()}")
    report.append("")
    
    # 多空总体统计
    report.append("【总体盈亏统计】")
    report.append(f"  多仓盈利单数: {results_df['long_win'].sum()} / {len(results_df)} ({results_df['long_win'].mean()*100:.1f}%)")
    report.append(f"  多仓平均收益: {results_df['long_pnl_pct'].mean():.4f}%")
    report.append(f"  空仓盈利单数: {results_df['short_win'].sum()} / {len(results_df)} ({results_df['short_win'].mean()*100:.1f}%)")
    report.append(f"  空仓平均收益: {results_df['short_pnl_pct'].mean():.4f}%")
    report.append("")
    
    # Top 10 组合类型
    report.append("【盈利最高组合类型 (Top 10)】")
    top_profit = summary_df.nlargest(10, '多仓平均收益%')
    for _, row in top_profit.iterrows():
        report.append(f"  {row['combo_type']}: 多仓胜率{row['多仓胜率']*100:.1f}% | 多仓均收益{row['多仓平均收益%']:.2f}% | 组合数{row['组合数量']}")
    report.append("")
    
    # 保存报告
    report_text = "\n".join(report)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
        f.write("\n\n")
        f.write("【详细组合类型统计】\n")
        f.write(summary_df.to_string(index=False))
    
    return report_text


def analyze_file(file_path, min_len=5, max_len=12):
    """
    分析单个K线数据文件
    """
    print(f"\n{'='*60}")
    print(f"开始分析: {file_path}")
    print(f"{'='*60}")
    
    # 读取数据
    df = pd.read_csv(file_path)
    print(f"读取数据: {len(df)} 条")
    
    # 解析时间
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
    elif 'date' in df.columns:
        df['datetime'] = pd.to_datetime(df['date'])
    
    # K线分析
    print("正在进行K线性质和关系分析...")
    df = analyze_kline(df)
    
    # 组合分析
    print("正在进行K线组合分析...")
    results_df = analyze_combinations(df, min_len, max_len)
    
    # 汇总统计
    print("正在汇总统计...")
    summary_df = summarize_results(results_df)
    
    # 输出路径
    base_name = os.path.basename(file_path).replace('.csv', '')
    output_dir = os.path.dirname(file_path)
    
    # 保存处理后的数据
    processed_path = os.path.join(output_dir, f"{base_name}_processed.csv")
    df.to_csv(processed_path, index=False, encoding='utf-8-sig')
    print(f"已保存处理后数据: {processed_path}")
    
    # 保存组合结果
    results_path = os.path.join(output_dir, f"{base_name}_combinations.csv")
    results_df.to_csv(results_path, index=False, encoding='utf-8-sig')
    print(f"已保存组合结果: {results_path}")
    
    # 保存汇总统计
    summary_path = os.path.join(output_dir, f"{base_name}_summary.csv")
    summary_df.to_csv(summary_path, index=False, encoding='utf-8-sig')
    print(f"已保存汇总统计: {summary_path}")
    
    # 生成报告
    report_path = os.path.join(output_dir, f"{base_name}_report.txt")
    report_text = generate_report(df, results_df, summary_df, report_path)
    print(f"已保存分析报告: {report_path}")
    
    print(f"\n{'='*60}")
    print("分析完成!")
    print(f"{'='*60}")
    
    # 打印报告摘要
    print("\n" + report_text)
    
    return df, results_df, summary_df


# ==================== 主程序 ====================

if __name__ == "__main__":
    import sys
    
    # 默认分析 data 目录下的所有CSV
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    if len(sys.argv) > 1:
        # 命令行指定文件
        file_path = sys.argv[1]
        analyze_file(file_path)
    else:
        # 分析data目录下所有文件
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv') and '_processed' not in f]
        
        for csv_file in csv_files:
            file_path = os.path.join(data_dir, csv_file)
            analyze_file(file_path)
            print("\n")
