"""
下载沪镍2605、沪锡2605、沪金2604、沪银2606 近一个月1分钟K线数据
数据来源：新浪财经（通过 akshare）
"""

import akshare as ak
import pandas as pd
import os
from datetime import datetime, timedelta

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 合约列表：(新浪代码, 描述)
# 上期所：NI=沪镍, SN=沪锡, AU=沪金, AG=沪银
CONTRACTS = [
    ("ni2605", "沪镍2605"),
    ("sn2605", "沪锡2605"),
    ("au2604", "沪金2604"),
    ("ag2606", "沪银2606"),
]

# 近一个月时间范围
end_date = datetime.today()
start_date = end_date - timedelta(days=30)
print(f"时间范围: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
print("-" * 50)

for symbol, name in CONTRACTS:
    print(f"正在下载 {name} ({symbol}) ...")
    try:
        df = ak.futures_zh_minute_sina(symbol=symbol, period="1")
        if df is None or df.empty:
            print(f"  ⚠️  {name} 返回空数据，跳过")
            continue

        # 统一列名
        df.columns = [c.strip() for c in df.columns]
        print(f"  原始列名: {list(df.columns)}")

        # 时间列处理
        time_col = df.columns[0]
        df[time_col] = pd.to_datetime(df[time_col])
        df = df.rename(columns={time_col: "datetime"})
        df = df.sort_values("datetime").reset_index(drop=True)

        # 过滤近一个月
        mask = df["datetime"] >= pd.Timestamp(start_date.date())
        df_filtered = df[mask].copy()

        print(f"  总行数: {len(df)} | 近一个月: {len(df_filtered)} 条")
        if df_filtered.empty:
            print(f"  ⚠️  近一个月无数据，保存全量数据")
            df_filtered = df

        # 保存
        filename = f"{symbol}_1min_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        df_filtered.to_csv(filepath, index=False, encoding="utf-8-sig")
        print(f"  ✅ 已保存: {filepath}")
        print(f"  时间范围: {df_filtered['datetime'].min()} ~ {df_filtered['datetime'].max()}")

    except Exception as e:
        print(f"  ❌ {name} 下载失败: {e}")

    print()

print("=" * 50)
print("全部完成！")
