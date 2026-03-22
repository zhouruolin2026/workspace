"""
期货一分钟K线信号分析程序
功能：
1. 定义信号：买点K线前的K线形态构成信号
2. 信号分类：根据信号区的K线形态划分类型
3. 统计每种信号类型的胜率
4. 输出高胜率信号类型及其具体形态解释
5. 保存每种信号类型的明细数据
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from collections import defaultdict

# ==================== K线基础分析 ====================

def get_kline_category(row):
    """
    获取K线分类（大类）
    """
    o, h, l, c = row['open'], row['high'], row['low'], row['close']
    
    body = abs(c - o)
    total_range = h - l
    
    if total_range == 0:
        return "一字板"
    
    body_ratio = body / total_range
    is_up = c > o
    is_doji = body_ratio < 0.1
    
    if is_doji:
        return "十字星"
    elif is_up:
        if body_ratio > 0.6:
            return "大阳"
        elif body_ratio > 0.3:
            return "中阳"
        else:
            return "小阳"
    else:
        if body_ratio > 0.6:
            return "大阴"
        elif body_ratio > 0.3:
            return "中阴"
        else:
            return "小阴"


def get_kline_detail_type(row):
    """
    获取K线详细类型
    """
    o, h, l, c = row['open'], row['high'], row['low'], row['close']
    
    body = abs(c - o)
    total_range = h - l
    
    if total_range == 0:
        return "一字板"
    
    upper_shadow = h - max(o, c)
    lower_shadow = min(o, c) - l
    body_ratio = body / total_range
    
    is_up = c > o
    is_doji = body_ratio < 0.1
    
    if is_doji:
        if upper_shadow > 0.3 * total_range and lower_shadow > 0.3 * total_range:
            return "十字星"
        elif upper_shadow > 0.3 * total_range:
            return "倒T"
        elif lower_shadow > 0.3 * total_range:
            return "T字"
        return "小十字"
    
    # 带长上影
    if upper_shadow > 0.5 * total_range:
        return "长上影阳" if is_up else "长上影阴"
    
    # 带长下影
    if lower_shadow > 0.5 * total_range:
        return "长下影阳" if is_up else "长下影阴"
    
    # 普通K线
    if is_up:
        if body_ratio > 0.6:
            return "大阳"
        elif body_ratio > 0.3:
            return "中阳"
        else:
            return "小阳"
    else:
        if body_ratio > 0.6:
            return "大阴"
        elif body_ratio > 0.3:
            return "中阴"
        else:
            return "小阴"


def analyze_signal(df, signal_len=3, min_hold=2):
    """
    分析信号
    signal_len: 信号区K线数量（买点前的K线）
    min_hold: 最少持有K线数量
    
    返回: 信号类型、买点、卖点、盈亏
    """
    results = []
    n = len(df)
    
    # 买点位置：从第 signal_len+1 根开始，到倒数第 min_hold 根结束
    for buy_idx in range(signal_len, n - min_hold):
        # 信号区（买点前的K线）
        signal_df = df.iloc[buy_idx - signal_len:buy_idx].reset_index(drop=True)
        
        # 买点K线
        buy_row = df.iloc[buy_idx]
        
        # 卖点（持有到最后）
        sell_df = df.iloc[buy_idx + 1:].reset_index(drop=True)
        
        if len(sell_df) < 1:
            continue
        
        # 卖点的收盘价（最后一根K线的收盘价）
        sell_price = sell_df.iloc[-1]['close']
        buy_price = buy_row['close']
        
        # 多仓盈亏
        long_pnl = sell_price - buy_price
        long_pnl_pct = (sell_price - buy_price) / buy_price * 100
        long_win = long_pnl > 0
        
        # 空仓盈亏
        short_pnl = buy_price - sell_price
        short_pnl_pct = (buy_price - sell_price) / buy_price * 100
        short_win = short_pnl > 0
        
        # 信号分类
        signal_type = classify_signal(signal_df)
        
        results.append({
            'signal_type': signal_type,
            'signal_klines': signal_len,
            'buy_idx': buy_idx,
            'buy_time': buy_row['datetime'],
            'buy_price': buy_price,
            'sell_time': sell_df.iloc[-1]['datetime'],
            'sell_price': sell_price,
            'hold_klines': len(sell_df),
            'long_pnl': long_pnl,
            'long_pnl_pct': long_pnl_pct,
            'long_win': long_win,
            'short_pnl': short_pnl,
            'short_pnl_pct': short_pnl_pct,
            'short_win': short_win,
            # 信号区详情
            'signal_detail': get_signal_detail(signal_df),
            # 买点详情
            'buy_type': buy_row.get('K线性质', get_kline_detail_type(buy_row)),
        })
    
    return pd.DataFrame(results)


def classify_signal(signal_df):
    """
    根据信号区的K线形态分类
    """
    if len(signal_df) < 2:
        return "信号太短"
    
    # 获取各类K线数量
    categories = [get_kline_category(row) for _, row in signal_df.iterrows()]
    
    # 统计
    yang_count = sum(1 for c in categories if '阳' in c)
    yin_count = sum(1 for c in categories if '阴' in c)
    xing_count = sum(1 for c in categories if '十' in c or '星' in c)
    
    # 计算整体涨跌幅
    first_close = signal_df.iloc[0]['close']
    last_close = signal_df.iloc[-1]['close']
    total_change = (last_close - first_close) / first_close * 100
    
    # 趋势判断
    if total_change > 1:
        trend = "上涨"
    elif total_change < -1:
        trend = "下跌"
    else:
        trend = "震荡"
    
    # 连续性判断
    consecutive_up = 0
    consecutive_down = 0
    for i in range(1, len(signal_df)):
        if signal_df.iloc[i]['close'] > signal_df.iloc[i-1]['close']:
            consecutive_up += 1
        if signal_df.iloc[i]['close'] < signal_df.iloc[i-1]['close']:
            consecutive_down += 1
    
    # 分类逻辑
    # 1. 连续上涨/下跌
    if consecutive_up >= len(signal_df) - 1:
        return f"连续上涨{len(signal_df)}K"
    if consecutive_down >= len(signal_df) - 1:
        return f"连续下跌{len(signal_df)}K"
    
    # 2. 回调/反弹（先涨后跌 或 先跌后涨）
    if categories[0] in ['大阳', '中阳', '小阳'] and categories[-1] in ['大阴', '中阴', '小阴']:
        return "冲高回落"
    if categories[0] in ['大阴', '中阴', '小阴'] and categories[-1] in ['大阳', '中阳', '小阳']:
        return "探底回升"
    
    # 3. 震荡上行/下行
    if trend == "上涨" and yang_count > yin_count:
        return "震荡上涨"
    if trend == "下跌" and yin_count > yang_count:
        return "震荡下跌"
    
    # 4. 横盘整理
    if abs(total_change) < 0.5:
        return "横盘整理"
    
    # 5. 高位/低位十字星
    if xing_count >= 1:
        if trend == "上涨":
            return "高位十字星"
        elif trend == "下跌":
            return "低位十字星"
        return "中位十字星"
    
    # 6. 阴阳交错
    if yang_count > 0 and yin_count > 0:
        return "阴阳交错"
    
    # 默认
    return f"{trend}信号"


def get_signal_detail(signal_df):
    """
    获取信号详细描述
    """
    if len(signal_df) == 0:
        return ""
    
    details = []
    for i, row in signal_df.iterrows():
        ktype = get_kline_detail_type(row)
        change = (row['close'] - row['open']) / row['open'] * 100
        details.append(f"{i+1}#{ktype}{change:+.2f}%")
    
    return ";".join(details)


# ==================== 信号分析主程序 ====================

def full_signal_analysis(df, min_signal_len=2, max_signal_len=5):
    """
    完整信号分析
    对5-12根K线的组合，尝试不同的信号长度
    """
    all_results = []
    
    # 组合长度从5到12
    for combo_len in range(5, 13):
        print(f"  分析组合长度 {combo_len}K...")
        
        # 滑动窗口提取组合
        for start_idx in range(len(df) - combo_len + 1):
            combo = df.iloc[start_idx:start_idx + combo_len].reset_index(drop=True)
            
            # 对组合中每个位置作为买点进行测试
            # 买点位置：信号区之后，至少保留2根K线作为持有
            for buy_pos in range(min_signal_len, combo_len - 1):
                # 信号区
                signal_part = combo.iloc[:buy_pos]
                # 买点
                buy_row = combo.iloc[buy_pos]
                # 持有区（卖点）
                hold_part = combo.iloc[buy_pos + 1:]
                
                if len(hold_part) < 1:
                    continue
                
                # 买点价格
                buy_price = buy_row['close']
                # 卖点价格（最后收盘价）
                sell_price = hold_part.iloc[-1]['close']
                
                # 多仓
                long_pnl_pct = (sell_price - buy_price) / buy_price * 100
                long_win = long_pnl_pct > 0
                
                # 空仓
                short_pnl_pct = (buy_price - sell_price) / buy_price * 100
                short_win = short_pnl_pct > 0
                
                # 信号分类
                signal_type = classify_signal(signal_part)
                
                all_results.append({
                    'combo_len': combo_len,
                    'start_idx': start_idx,
                    'buy_pos': buy_pos,
                    'signal_len': buy_pos,
                    'signal_type': signal_type,
                    'buy_time': buy_row['datetime'],
                    'buy_price': buy_price,
                    'sell_time': hold_part.iloc[-1]['datetime'],
                    'sell_price': sell_price,
                    'hold_len': len(hold_part),
                    'long_pnl_pct': long_pnl_pct,
                    'long_win': long_win,
                    'short_pnl_pct': short_pnl_pct,
                    'short_win': short_win,
                    'signal_detail': get_signal_detail(signal_part),
                    'buy_type': get_kline_detail_type(buy_row),
                })
    
    return pd.DataFrame(all_results)


def summarize_signals(results_df):
    """
    汇总信号统计
    """
    if results_df.empty:
        return pd.DataFrame()
    
    summary = results_df.groupby('signal_type').agg({
        'combo_len': ['count', 'mean'],
        'long_pnl_pct': ['mean', 'std', 'min', 'max'],
        'long_win': ['sum', 'mean'],
        'short_pnl_pct': ['mean', 'std', 'min', 'max'],
        'short_win': ['sum', 'mean'],
        'buy_pos': 'mean',
    }).round(4)
    
    summary.columns = [
        '信号数量', '平均组合长度',
        '多仓均收益%', '多仓标准差', '多仓最小%', '多仓最大%',
        '多仓盈利数', '多仓胜率',
        '空仓均收益%', '空仓标准差', '空仓最小%', '空仓最大%',
        '空仓盈利数', '空仓胜率',
        '平均买点位置',
    ]
    
    summary = summary.reset_index()
    
    # 按信号数量排序
    summary = summary.sort_values('信号数量', ascending=False)
    
    return summary


def get_signal_description(signal_type):
    """
    获取信号类型的中文解释
    """
    descriptions = {
        "连续上涨3K": "连续3根K线收盘价依次上涨，表示强劲上涨趋势",
        "连续上涨4K": "连续4根K线收盘价依次上涨，表示强劲上涨趋势",
        "连续上涨5K": "连续5根K线收盘价依次上涨，表示强劲上涨趋势",
        "连续下跌3K": "连续3根K线收盘价依次下跌，表示强劲下跌趋势",
        "连续下跌4K": "连续4根K线收盘价依次下跌，表示强劲下跌趋势",
        "连续下跌5K": "连续5根K线收盘价依次下跌，表示强劲下跌趋势",
        "冲高回落": "信号区首根K线收阳（上涨），但最后收阴（下跌），表示上涨乏力可能反转",
        "探底回升": "信号区首根K线收阴（下跌），但最后收阳（上涨），表示下跌获支撑可能反转",
        "震荡上涨": "整体呈上涨趋势，但过程中有回调，整体涨幅大于1%",
        "震荡下跌": "整体呈下跌趋势，但过程中有反弹，整体跌幅大于1%",
        "横盘整理": "信号区整体涨跌幅小于0.5%，表示盘整状态",
        "高位十字星": "在上涨趋势中出现十字星，表示可能见顶",
        "低位十字星": "在下跌趋势中出现十字星，表示可能见底",
        "中位十字星": "在震荡过程中出现十字星，表示方向选择",
        "阴阳交错": "阳线阴线交替出现，表示多空博弈激烈",
    }
    
    return descriptions.get(signal_type, f"信号类型: {signal_type}")


def generate_report(df, results_df, summary_df, output_path):
    """
    生成分析报告
    """
    report = []
    report.append("=" * 90)
    report.append("                     期货一分钟K线信号分析报告")
    report.append("=" * 90)
    report.append("")
    
    # 基本信息
    report.append("【数据概况】")
    report.append(f"  数据时间范围: {df['datetime'].min()} ~ {df['datetime'].max()}")
    report.append(f"  总K线数量: {len(df)}")
    report.append("")
    
    # 信号分析结果
    report.append("【信号分析统计】")
    report.append(f"  总信号数量: {len(results_df)}")
    report.append(f"  信号类型数量: {results_df['signal_type'].nunique()}")
    report.append("")
    
    # 总体胜率
    report.append("【总体胜率】")
    report.append(f"  多仓胜率: {results_df['long_win'].mean()*100:.2f}%")
    report.append(f"  空仓胜率: {results_df['short_win'].mean()*100:.2f}%")
    report.append("")
    
    # Top 10 信号类型（按数量）
    report.append("=" * 90)
    report.append("【信号类型排名 Top 10（按数量）】")
    report.append("=" * 90)
    
    top10 = summary_df.head(10)
    for rank, (_, row) in enumerate(top10.iterrows(), 1):
        signal_type = row['signal_type']
        desc = get_signal_description(signal_type)
        
        report.append(f"\n【第{rank}名】 {signal_type}")
        report.append(f"  信号解释: {desc}")
        report.append(f"  信号数量: {int(row['信号数量'])} 个")
        report.append(f"  多仓胜率: {row['多仓胜率']*100:.2f}% ({int(row['多仓盈利数'])}/{int(row['信号数量'])})")
        report.append(f"  多仓平均收益: {row['多仓均收益%']:.4f}%")
        report.append(f"  空仓胜率: {row['空仓胜率']*100:.2f}% ({int(row['空仓盈利数'])}/{int(row['信号数量'])})")
        report.append(f"  空仓平均收益: {row['空仓均收益%']:.4f}%")
    
    # 按胜率排序的Top 10
    report.append("\n" + "=" * 90)
    report.append("【多仓胜率 Top 10（信号数量≥50）】")
    report.append("=" * 90)
    
    top_win = summary_df[summary_df['信号数量'] >= 50].nlargest(10, '多仓胜率')
    for rank, (_, row) in enumerate(top_win.iterrows(), 1):
        signal_type = row['signal_type']
        desc = get_signal_description(signal_type)
        
        report.append(f"\n第{rank}名: {signal_type}")
        report.append(f"  解释: {desc}")
        report.append(f"  数量: {int(row['信号数量'])} | 多仓胜率: {row['多仓胜率']*100:.2f}% | 均收益: {row['多仓均收益%']:.4f}%")
    
    # 保存报告
    report_text = "\n".join(report)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    return report_text


def save_signal_details(results_df, summary_df, output_dir):
    """
    保存每种信号类型的明细数据
    """
    # 取Top 10信号类型
    top10_types = summary_df.head(10)['signal_type'].tolist()
    
    saved_files = []
    
    for signal_type in top10_types:
        # 筛选该类型的信号
        type_df = results_df[results_df['signal_type'] == signal_type].copy()
        
        if len(type_df) == 0:
            continue
        
        # 简化列名，保存
        save_cols = ['combo_len', 'buy_pos', 'signal_len', 'buy_time', 'buy_price', 
                     'sell_time', 'sell_price', 'hold_len',
                     'long_pnl_pct', 'long_win', 'short_pnl_pct', 'short_win',
                     'signal_detail', 'buy_type']
        
        # 清理列名
        type_df = type_df[[c for c in save_cols if c in type_df.columns]]
        
        # 文件名
        safe_name = signal_type.replace("/", "_").replace(" ", "_")
        filename = f"signal_{safe_name}.csv"
        filepath = os.path.join(output_dir, filename)
        
        type_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        saved_files.append((filename, len(type_df)))
    
    return saved_files


def analyze_file(file_path):
    """
    分析单个文件
    """
    print(f"\n{'='*70}")
    print(f"开始分析: {file_path}")
    print(f"{'='*70}")
    
    # 读取数据
    df = pd.read_csv(file_path)
    print(f"读取数据: {len(df)} 条")
    
    # 解析时间
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
    elif 'date' in df.columns:
        df['datetime'] = pd.to_datetime(df['date'])
    
    # 添加K线类型
    print("添加K线类型...")
    df['K线分类'] = df.apply(get_kline_category, axis=1)
    df['K线详细'] = df.apply(get_kline_detail_type, axis=1)
    
    # 完整信号分析
    print("进行信号分析（5-12根K线组合，买点前2-5根为信号区）...")
    results_df = full_signal_analysis(df, min_signal_len=2, max_signal_len=5)
    print(f"  共生成 {len(results_df)} 个信号")
    
    # 汇总统计
    print("汇总统计...")
    summary_df = summarize_signals(results_df)
    
    # 输出路径
    base_name = os.path.basename(file_path).replace('.csv', '')
    output_dir = os.path.dirname(file_path)
    
    # 保存结果
    results_path = os.path.join(output_dir, f"{base_name}_signals.csv")
    results_df.to_csv(results_path, index=False, encoding='utf-8-sig')
    print(f"已保存信号结果: {results_path}")
    
    summary_path = os.path.join(output_dir, f"{base_name}_signal_summary.csv")
    summary_df.to_csv(summary_path, index=False, encoding='utf-8-sig')
    print(f"已保存汇总: {summary_path}")
    
    # 生成报告
    report_path = os.path.join(output_dir, f"{base_name}_signal_report.txt")
    report_text = generate_report(df, results_df, summary_df, report_path)
    print(f"已保存报告: {report_path}")
    
    # 保存Top 10信号类型明细
    print("保存信号类型明细...")
    saved = save_signal_details(results_df, summary_df, output_dir)
    for fname, count in saved:
        print(f"  已保存: {fname} ({count}条)")
    
    print(f"\n{'='*70}")
    print("分析完成!")
    print(f"{'='*70}")
    
    # 打印报告摘要
    print("\n" + report_text)
    
    return results_df, summary_df


# ==================== 主程序 ====================

if __name__ == "__main__":
    import sys
    
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        analyze_file(file_path)
    else:
        # 分析所有原始数据文件
        csv_files = [f for f in os.listdir(data_dir) 
                     if f.endswith('.csv') and '_processed' not in f 
                     and '_signals' not in f and '_signal' not in f]
        
        for csv_file in csv_files:
            file_path = os.path.join(data_dir, csv_file)
            analyze_file(file_path)
            print("\n" + "="*70 + "\n")
