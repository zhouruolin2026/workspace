# pandas学习

import pandas as pd

# 示例表（我们后续都用这个 df 演示）
df = pd.DataFrame({
    "id": [1, 2, 3, 4, 5],
    "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
    "age": [25, 30, 35, 28, 22],
    "city": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Hangzhou"],
    "score": [88.5, 92.0, 78.5, 95.0, 65.0]
})

print(df)

# select id,name from df
print(df[["id", "name"]])

# select id, name as s_name from df
print(df[["id", "name"]].rename(columns={"name": "s_name"})) # type: ignore

# select id, age % 2 as jiou from df;
df["jiou"] = df["age"] % 2
print(df[["id", "age", "jiou"]])

# left join