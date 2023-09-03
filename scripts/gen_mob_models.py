import pandas as pd

# 读取csv文件
df = pd.read_csv('scripts/models.csv')

# 筛选出dtype为mob的数据
df_mob = df[df['dtype'] == 'mob']

# 将筛选后的数据写入新的csv文件
df_mob.to_csv('scripts/mob_models.csv', index=False)

# 读取mob_models.csv文件
df_mob = pd.read_csv('scripts/mob_models.csv')

# 对model字段进行去重，对ver_name和brand字段进行合并
df_mob_unique = df_mob.groupby('model').agg({'ver_name': ' '.join, 'brand': 'first'}).reset_index()

# 将处理后的数据写入新的csv文件
df_mob_unique.to_csv('scripts/mob_models_unique.csv', index=False)

