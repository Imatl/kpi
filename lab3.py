from spyre import server
import pandas as pd
from datetime import datetime
import urllib.request
import seaborn as sns
import matplotlib.pyplot as plt
import os

def dwn(i, y1, y2):
    url = f'https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={i}&year1={y1}&year2={y2}&type=Mean'
    wp = urllib.request.urlopen(url)
    text = wp.read()

    if not os.path.exists('data'):
        os.makedirs('data')

    now = datetime.now()
    date_and_time_time = now.strftime('%d-%m-%Y_%H-%M-%S')
    out = open(f'data/NOAA_ID_{i}_{date_and_time_time}.csv', 'wb')
    out.write(text)
    out.close()

def load_single_csv(file_path):
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'AreaID']
    df = pd.read_csv(file_path, header=1, names=headers)
    return df


user_input = input("wanna download data? (y/n): ")
if user_input == "y":
    for i in range(1, 28):
        dwn(i, 2000, 2020)

file_path = 'data2/VHI_index.csv'
if os.path.exists(file_path):
    df = load_single_csv(file_path)
else:
    df = None
    print(f"Файл {file_path} не найден")


class WebApp(server.App):
    title = "NOAA visualization"

    inputs = [{"type": "dropdown",
                "label": "Region",
                "options": [{"label": "Вінницька", "value": "1"},
                            {"label": "Волинська", "value": "2"},
                            {"label": "Дніпропетровська", "value": "3"},
                            {"label": "Донецька", "value": "4"},
                            {"label": "Житомирська", "value": "5"},
                            {"label": "Закарпатська", "value": "6"},
                            {"label": "Запорізька", "value": "7"},
                            {"label": "Івано-Франківська", "value": "8"},
                            {"label": "Київська", "value": "9"},
                            {"label": "Кіровоградська", "value": "10"},
                            {"label": "Луганська", "value": "11"},
                            {"label": "Львівська", "value": "12"},
                            {"label": "Миколаївська", "value": "13"},
                            {"label": "Одеська", "value": "14"},
                            {"label": "Полтавська", "value": "15"},
                            {"label": "Рівенська", "value": "16"},
                            {"label": "Сумська", "value": "17"},
                            {"label": "Тернопільська", "value": "18"},
                            {"label": "Харківська", "value": "19"},
                            {"label": "Херсонська", "value": "20"},
                            {"label": "Хмельницька", "value": "21"},
                            {"label": "Черкаська", "value": "22"},
                            {"label": "Чернівецька", "value": "23"},
                            {"label": "Чернігівська", "value": "24"},
                            {"label": "Республіка Крим", "value": "25"},
                            {"label": "Севастополь", "value": "26"},
                            {"label": "КиЇв", "value": "27"}],
                 "key": "region",
                 "action_id": "update_data"},
              {"type": 'text',
                "key": 'week1',
                "label": 'min week',
                "value": '1',
                "action_id": 'update_data'},
              {"type": 'text',
                "key": 'week2',
                "label": 'max week',
                "value": '52',
                "action_id": 'update_data'},
              {"type": 'text',
                "key": 'year1',
                "label": 'min_year',
                "value": '2001',
                "action_id": 'update_data'},
              {"type": 'text',
                "key": 'year2',
                "label": 'max_year',
                "value": '2019',
                "action_id": 'update_data'},
              {"type": 'dropdown',
               "label": 'NOAA data dropdown',
               "options": [{"label": "VHI", "value":"VHI"},
                           {"label": "VCI", "value":"VCI"},
                           {"label": "TCI", "value":"TCI"}],
               "key": 'indicator',
               "action_id": "update_data"}]
    
    controls = [{"type": "hidden",
                 "id": "update_data"}]

    tabs = ["Table", "Plot"]

    outputs = [{"type": "table",
                 "id": "table_id",
                 "control_id": "update_data",
                 "tab": "Table",
                 "on_page_load": True},
               {"type": "plot",
                 "id": "plot",
                 "control_id": "update_data",
                 "tab": "Plot"}]
    
    def getTable(self, params):
        global df
        if df is None:
            return pd.DataFrame()

        w1 = int(params["week1"])
        w2 = int(params["week2"])
        y1 = int(params["year1"])
        y2 = int(params["year2"])
        region = int(params["region"])
        indicator = params["indicator"]

        required_columns = [indicator, 'Year', 'Week', 'AreaID']
        for col in required_columns:
            if col not in df.columns:
                print(f"Столбец {col} отсутствует в данных.")
                print("Все столбцы данных:", df.columns)
                return pd.DataFrame()

        result_df = df[[indicator, 'Year', 'Week', 'AreaID']]
        result_df = result_df[(df['AreaID'] == region)]
        result_df = result_df[df['Year'].between(y1, y2)]
        result_df = result_df[(df["Week"] >= w1) & (df["Week"] <= w2)]
        
        print("Фильтрованные данные:")
        print(result_df.head())
        
        return result_df

    def getPlot(self, params):
        # global df
        # if df is None:
        #     return None

        indicator = params["indicator"]
        data = self.getTable(params)
        if data.empty:
            print("Данные для графика отсутствуют.")
            return None

        color_palette = sns.color_palette("husl", len(data['Year'].unique()))
        plt_obj = None
        for i, (year, year_data) in enumerate(data.groupby('Year')):
            plt_obj = year_data.plot(x='Week', y=indicator, label=year, color=color_palette[i], ax=plt_obj)
        plt.legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid()

        plot = plt_obj.get_figure()
        plot.set_figwidth(12)
        plot.set_figheight(8)
        return plot

app = WebApp()
app.launch(port=8800)
