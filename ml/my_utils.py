from mypackage.entity.solar import analyze_combine_data_solar
from mypackage.entity.solar_processed import solar_processed
from mypackage.entity.transform import *
from mypackage.entity.wind import analyze_combine_data_wind
from mypackage.entity.wind_processed import wind_processed
from mypackage.process_data.solar_sliding_window_prediction import solar_predict
from mypackage.process_data.wind_sliding_window_prediction import wind_predict


def run_according_to_category(energy_category, raw_file_paths):

    assert energy_category is not None
    assert raw_file_paths is not None

    raw_output_path = "mypackage/process_data/data/input/"
    # raw_output_path = "C:\\Users\yhh\PycharmProjects\FlaskProject\mypackage\process_data\data\input"
    raw_file_path, json_path, txt_path = raw_file_paths[0], raw_file_paths[1], raw_file_paths[2]
    original_path = convert_to_csv(raw_file_path, raw_output_path)
    forecast_path = f"mypackage/process_data/data/output/{energy_category}_output.csv"
    # json_path = f"mypackage/entity/{energy_category}/json"
    # txt_path = f"mypackage/entity/{energy_category}/txt"

    try:
        if energy_category == 'solar':
            solar_predict(raw_file_path)
            solar_processed(original_path, forecast_path, json_path)
            analyze_combine_data_solar(original_path, forecast_path, txt_path)

        elif energy_category == 'wind':
            wind_predict(raw_file_path)
            wind_processed(original_path, forecast_path, json_path)
            analyze_combine_data_wind(original_path, forecast_path, txt_path)

    except Exception as e:
        raise e

    print(111)

# run_according_to_category('solar', "C:\\Users\\yhh\\PycharmProjects\\FlaskProject\\mypackage\\process_data\\data\\input\\solar_input.csv")
# run_according_to_category('wind', "C:\\Users\\yhh\\PycharmProjects\\FlaskProject\\mypackage\\process_data\\data\\input\\wind_input.csv")