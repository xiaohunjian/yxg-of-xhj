import pandas as pd
import os as os
from datetime import datetime
import json


def solar_processed(original_path,forecast_path,json_dir):
    # 1. 读取两文件数据，并转换格式
    df_original = pd.read_csv(original_path)
    df_original['date'] = pd.to_datetime(df_original['date'])
    df_original_perday = df_original[-96:].copy()
    df_original_perweek = df_original[-672:].copy()
    df_original_permonth = df_original[-2880:].copy()
    df_original_perseason = df_original[-8640:].copy()

    df_forecast = pd.read_csv(forecast_path)
    df_forecast['time'] = pd.to_datetime(df_forecast['time'])
    df_forecast_perday = df_forecast[0:96].copy()
    df_forecast_perweek = df_forecast[0:672].copy()
    df_forecast_permonth = df_forecast[0:2880].copy()

    # 2. 关键太阳能数据

    # 计算相对湿度
    avg_relative_humidity = df_original.groupby(df_original['date'].dt.date)['Relative humidity (%)'].mean()
    part1 = len([p for p in avg_relative_humidity if 0 <= p < 20])
    part2 = len([p for p in avg_relative_humidity if 20 <= p < 40])
    part3 = len([p for p in avg_relative_humidity if 40 <= p < 60])
    part4 = len([p for p in avg_relative_humidity if 60 <= p < 80])
    part5 = len([p for p in avg_relative_humidity if 80 <= p <= 100])

    total = part1 + part2 + part3 + part4 + part5
    per1 = round(part1 * 100 / total, 2)
    per2 = round(part2 * 100 / total, 2)
    per3 = round(part3 * 100 / total, 2)
    per4 = round(part4 * 100 / total, 2)
    per5 = round(100 - per1 - per2 - per3 - per4, 2)

    # 计算总太阳辐射度
    avg_total_irradiance_perweek = df_original_perweek.groupby(df_original_perweek['date'].dt.date)[
        'Total solar irradiance (W/m2)'].mean()
    avg_total_irradiance_permonth = df_original_permonth.groupby(df_original_permonth['date'].dt.date)[
        'Total solar irradiance (W/m2)'].mean()
    avg_total_irradiance_perseason = df_original_perseason.groupby(df_original['date'].dt.date)[
        'Total solar irradiance (W/m2)'].mean()

    # 计算空气温度
    avg_temperature_perweek = df_original_perweek.groupby(df_original_perweek['date'].dt.date)[
        'Air temperature  (°C) '].mean()
    avg_temperature_permonth = df_original_permonth.groupby(df_original_permonth['date'].dt.date)[
        'Air temperature  (°C) '].mean()
    avg_temperature_perseason = df_original_perseason.groupby(df_original['date'].dt.date)[
        'Air temperature  (°C) '].mean()

    # 直射辐射度
    avg_irradiance_perweek = df_original_perweek.groupby(df_original_perweek['date'].dt.date)[
        'Direct normal irradiance (W/m2)'].mean()
    avg_irradiance_permonth = df_original_permonth.groupby(df_original_permonth['date'].dt.date)[
        'Direct normal irradiance (W/m2)'].mean()
    avg_irradiance_perseason = df_original_perseason.groupby(df_original['date'].dt.date)[
        'Direct normal irradiance (W/m2)'].mean()

    # 计算原始数据输出功率
    avg_power_perweek = df_original_perweek.groupby(df_original_perweek['date'].dt.date)['power'].mean()
    avg_power_permonth = df_original_permonth.groupby(df_original_permonth['date'].dt.date)['power'].mean()
    avg_power_perseason = df_original_perseason.groupby(df_original['date'].dt.date)['power'].mean()

    # 计算预测数据输出功率
    daily_avg_power = df_forecast.groupby(df_forecast['time'].dt.date)['power'].mean()
    daily_avg_power_perweek = df_forecast_perweek.groupby(df_forecast_perweek['time'].dt.date)['power'].mean()
    daily_avg_power_permonth = df_forecast_permonth.groupby(df_forecast_permonth['time'].dt.date)['power'].mean()

    # 3. 转换为字典格式

    # 总太阳能辐射度
    total_irradiance = {
        "一天": [round(x, 2) for x in df_original_perday['Total solar irradiance (W/m2)'][::4]],
        "一周": [round(x, 2) for x in avg_total_irradiance_perweek.tolist()],
        "一月": [round(x, 2) for x in avg_total_irradiance_permonth.tolist()],
        "一季度": [round(x, 2) for x in avg_total_irradiance_perseason.tolist()]
    }

    # 空气温度
    temperature = {
        "一天": [round(x, 2) for x in df_original_perday['Air temperature  (°C) '][::4]],
        "一周": [round(x, 2) for x in avg_temperature_perweek.tolist()],
        "一月": [round(x, 2) for x in avg_temperature_permonth.tolist()],
        "一季度": [round(x, 2) for x in avg_temperature_perseason.tolist()]
    }

    # 直射辐射度
    irradiance = {
        "一天": [round(x, 2) for x in df_original_perday['Direct normal irradiance (W/m2)'][::4]],
        "一周": [round(x, 2) for x in avg_irradiance_perweek.tolist()],
        "一月": [round(x, 2) for x in avg_irradiance_permonth.tolist()],
        "一季度": [round(x, 2) for x in avg_irradiance_perseason.tolist()]
    }

    # 原始数据输出功率
    original_power = {
        "一天": [round(x, 2) for x in df_original_perday['power'][::4]],
        "一周": [round(x, 2) for x in avg_power_perweek.tolist()],
        "一月": [round(x, 2) for x in avg_power_permonth.tolist()],
        "一季度": [round(x, 2) for x in avg_power_perseason.tolist()]
    }

    # 预测数据输出功率
    forecast_power = {
        "一天": [round(x, 2) for x in df_forecast_perday['power'][::4]],
        "一周": [round(x, 2) for x in daily_avg_power_perweek.tolist()],
        "一月": [round(x, 2) for x in daily_avg_power_permonth.tolist()],
        "一季度": [round(x, 2) for x in daily_avg_power.tolist()]
    }

    # 转换报告
    report = {
        "data": {
            "pieChart": {
                "data": [
                    {"value": per1, "name": "[0,20)"},
                    {"value": per2, "name": "[20,40)"},
                    {"value": per3, "name": "[40,60)"},
                    {"value": per4, "name": "[60,80)"},
                    {"value": per5, "name": "[80,100]"}
                ]
            },
            "lineChart": {
                "seriesData1": {
                    "一天": [round(x, 2) for x in df_original_perday['Total solar irradiance (W/m2)'][::4]],
                    "一周": [round(x, 2) for x in avg_total_irradiance_perweek.tolist()],
                    "一月": [round(x, 2) for x in avg_total_irradiance_permonth.tolist()],
                    "一季度": [round(x, 2) for x in avg_total_irradiance_perseason.tolist()],
                },
                "seriesData2": {
                    "一天": [round(x, 2) for x in df_original_perday['Air temperature  (°C) '][::4]],
                    "一周": [round(x, 2) for x in avg_temperature_perweek.tolist()],
                    "一月": [round(x, 2) for x in avg_temperature_permonth.tolist()],
                    "一季度": [round(x, 2) for x in avg_temperature_perseason.tolist()],
                },
                "seriesData3": {
                    "一天": [round(x, 2) for x in df_original_perday['Direct normal irradiance (W/m2)'][::4]],
                    "一周": [round(x, 2) for x in avg_irradiance_perweek.tolist()],
                    "一月": [round(x, 2) for x in avg_irradiance_permonth.tolist()],
                    "一季度": [round(x, 2) for x in avg_irradiance_perseason.tolist()],
                },
                "seriesData4": {
                    "一天": [round(x, 2) for x in df_original_perday['power'][::4]],
                    "一周": [round(x, 2) for x in avg_power_perweek.tolist()],
                    "一月": [round(x, 2) for x in avg_power_permonth.tolist()],
                    "一季度": [round(x, 2) for x in avg_power_perseason.tolist()],
                },
                "seriesData5": {
                    "一天": [round(x, 2) for x in df_forecast_perday['power'][::4]],
                    "一周": [round(x, 2) for x in daily_avg_power_perweek.tolist()],
                    "一月": [round(x, 2) for x in daily_avg_power_permonth.tolist()],
                    "一季度": [round(x, 2) for x in daily_avg_power.tolist()],
                }
            }
        }

    }
    base_name = os.path.basename(os.path.splitext(original_path)[0])
    output_file = json_dir  # 此处修改json文件名
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    

if __name__ == "__main__":
    original_csv = 'solar/original_data/solar1.csv' # 此处修改原始数据地址
    forecast_csv = 'solar/forecast_data/solar2.csv' # 此处修改预测数据地址
    json_dir = 'solar/json' # 此处修改json文件目录
    solar_processed(original_csv, forecast_csv,json_dir)