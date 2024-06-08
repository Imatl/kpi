import pandas as pd

file_path = 'VHI_index.csv'

# Загрузка файла и вывод первых строк
df = pd.read_csv(file_path)
print(df.head())
print(df.columns)
