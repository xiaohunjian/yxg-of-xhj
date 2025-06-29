import pandas as pd
import argparse
import os

def convert_to_csv(input_file, output_dir):
    """
    根据输入文件的类型，将其转换为CSV格式并保存
    
    参数:
    input_file (str): 输入文件的路径
    output_dir (str, optional): 输出CSV文件的目录，默认为None(与输入文件同目录)
    
    返回:
    str: 转换后的CSV文件路径
    """
    # 获取文件扩展名并转换为小写
    file_ext = os.path.splitext(input_file)[1].lower()
    
    # # 如果未指定输出目录，则使用输入文件所在目录
    # if not output_dir:
    #     output_dir = os.path.dirname(input_file)
    #
    # # 创建输出目录（如果不存在）
    # os.makedirs(output_dir, exist_ok=True)
    
    # 生成输出文件名（使用输入文件的基本名称）
    base_name = os.path.basename(os.path.splitext(input_file)[0])
    output_file = os.path.join(output_dir, f"{base_name}.csv")
    
    # 根据文件类型选择读取方法
    if file_ext == '.csv':
        df = pd.read_csv(input_file)
    elif file_ext == '.tsv':
        df = pd.read_csv(input_file, delimiter='\t')
    elif file_ext == '.txt':
        df = pd.read_csv(input_file)
    elif file_ext in ['.xls', '.xlsx']:
        df = pd.read_excel(input_file)
    else:
        raise ValueError(f"不支持的文件类型: {file_ext}")

    # 定义要重命名的列和新的列名
    columns_to_rename = {
        "Time(year-month-day h:m:s)": "date",
        "Power (MW)": "power"
    }

    # 只修改指定列的名称，保留其他列不变
    df = df.rename(columns=columns_to_rename)
    
    # 保存为CSV文件
    df.to_csv(output_file, index=False)
    return output_file


if __name__ == "__main__":
    input_file = "solar\data_user\Solar station site 4 (Nominal capacity-130MW).xlsx" # 此处修改输入文件的路径
    output_dir = 'solar/original_data' # 此处修改输出文件的目录
    convert_to_csv(input_file ,output_dir)