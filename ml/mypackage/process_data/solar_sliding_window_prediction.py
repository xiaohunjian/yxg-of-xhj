import numpy as np
import pandas as pd
import torch
import sys
import os
import argparse
from datetime import datetime, timedelta

# 添加Informer项目路径
sys.path.append(r'C:\Users\yijian\Desktop\project\yxg\ml\mypackage\process_data\Informer2020-main\Informer2020-main')
from exp.exp_informer import Exp_Informer
from utils.tools import StandardScaler


# 参数设置
parser = argparse.ArgumentParser(description='太阳能发电Informer滑动窗口预测')
parser.add_argument('--model', type=str, default='informer', help='模型类型')
parser.add_argument('--data', type=str, default='custom', help='数据集名称')
parser.add_argument('--root_path', type=str, default='mypackage/process_data/data/input', help='数据根目录')
parser.add_argument('--data_path', type=str, default='solar_input.csv', help='数据文件')
parser.add_argument('--features', type=str, default='M', help='预测任务类型')
parser.add_argument('--target', type=str, default='power', help='目标特征')
parser.add_argument('--freq', type=str, default='h', help='时间频率，h表示小时级(hourly)')
parser.add_argument('--checkpoints', type=str, default='./checkpoints/', help='模型检查点位置')
parser.add_argument('--seq_len', type=int, default=96, help='输入序列长度')
parser.add_argument('--label_len', type=int, default=48, help='标签序列长度')
parser.add_argument('--pred_len', type=int, default=24, help='预测序列长度，设为24表示6小时(15分钟×24=6小时)')
parser.add_argument('--enc_in', type=int, default=7, help='编码器输入大小')
parser.add_argument('--dec_in', type=int, default=7, help='解码器输入大小')
parser.add_argument('--c_out', type=int, default=1, help='输出大小')
parser.add_argument('--d_model', type=int, default=512, help='模型维度')
parser.add_argument('--n_heads', type=int, default=8, help='注意力头数')
parser.add_argument('--e_layers', type=int, default=2, help='编码器层数')
parser.add_argument('--d_layers', type=int, default=1, help='解码器层数')
parser.add_argument('--d_ff', type=int, default=2048, help='前馈网络维度')
parser.add_argument('--factor', type=int, default=3, help='ProbSparse注意力因子')
parser.add_argument('--distil', action='store_false', help='是否使用蒸馏', default=True)
parser.add_argument('--dropout', type=float, default=0.05, help='dropout率')
parser.add_argument('--attn', type=str, default='prob', help='注意力类型')
parser.add_argument('--embed', type=str, default='timeF', help='时间特征编码')
parser.add_argument('--activation', type=str, default='gelu', help='激活函数')
parser.add_argument('--output_attention', action='store_true', help='是否输出注意力')
parser.add_argument('--do_predict', action='store_true', help='是否预测未见过的未来数据')
parser.add_argument('--mix', action='store_false', help='是否使用混合注意力', default=True)
parser.add_argument('--cols', type=str, nargs='+', help='输入特征列')
parser.add_argument('--num_workers', type=int, default=0, help='数据加载器工作线程数')
parser.add_argument('--batch_size', type=int, default=32, help='批大小')
parser.add_argument('--use_gpu', type=bool, default=True, help='是否使用GPU')
parser.add_argument('--gpu', type=int, default=0, help='GPU编号')
parser.add_argument('--use_multi_gpu', action='store_true', help='是否使用多GPU', default=False)
parser.add_argument('--devices', type=str, default='0', help='设备ID')
parser.add_argument('--des', type=str, default='test', help='实验描述')
parser.add_argument('--detail_freq', type=str, default='h', help='预测时使用的时间频率')
parser.add_argument('--padding', type=int, default=0, help='padding类型')
parser.add_argument('--use_amp', action='store_true', help='使用自动混合精度训练', default=False)
parser.add_argument('--inverse', type=bool, default=True, help='是否反转转换，用于还原预测值到原始范围')
# 强制设置为True
args = parser.parse_args([])
args.inverse = True  # 强制设置为True

# 设置GPU
args.use_gpu = True if torch.cuda.is_available() and args.use_gpu else False
if args.use_gpu and args.use_multi_gpu:
    args.devices = args.devices.replace(' ', '')
    device_ids = args.devices.split(',')
    args.device_ids = [int(id_) for id_ in device_ids]
    args.gpu = args.device_ids[0]

# 设置预测天数和每天的时间步数
days_to_predict = 90  # 预测一个季度（90天）
steps_per_day = 96   # 每天96个时间步（15分钟间隔）
predictions_per_day = steps_per_day // args.pred_len  # 每天需要多少次预测

def is_nighttime_seasonal(month, hour):
    if month in [12, 1, 2]:  # 冬季
        return hour >= 18 or hour < 7  
    elif month in [3, 4, 5, 9, 10, 11]:  # 春秋季
        return hour >= 19 or hour < 6
    else:  # 夏季 (6, 7, 8)
        return hour >= 20 or hour < 5

def get_sunset_decay_factor_smooth(hour, minute, month):
    """
    获取平滑的日落衰减因子 - 分钟级线性插值
    """
    # 计算精确时间
    exact_time = hour + minute / 60.0
    
    if month in [11, 12, 1, 2]:  # 冬季
        if exact_time < 15.0:
            return 1.0
        elif 15.0 <= exact_time < 16.0:
            # 15:00-16:00 线性从100%降到85%
            progress = exact_time - 15.0
            return 1.0 - progress * 0.15
        elif 16.0 <= exact_time < 17.0:
            # 16:00-17:00 线性从85%降到60%
            progress = exact_time - 16.0
            return 0.85 - progress * 0.25
        elif 17.0 <= exact_time < 18.0:
            # 17:00-18:00 线性从60%降到25%
            progress = exact_time - 17.0
            return 0.6 - progress * 0.35
        elif 18.0 <= exact_time < 19.0:
            # 18:00-19:00 线性从25%降到5%
            progress = exact_time - 18.0
            return 0.25 - progress * 0.2
        else:
            return 0.05
    elif month in [3, 4, 9, 10]:  # 春秋季
        if exact_time < 16.0:
            return 1.0
        elif 16.0 <= exact_time < 17.0:
            progress = exact_time - 16.0
            return 1.0 - progress * 0.1
        elif 17.0 <= exact_time < 18.0:
            progress = exact_time - 17.0
            return 0.9 - progress * 0.2
        elif 18.0 <= exact_time < 19.0:
            progress = exact_time - 18.0
            return 0.7 - progress * 0.4
        elif 19.0 <= exact_time < 20.0:
            progress = exact_time - 19.0
            return 0.3 - progress * 0.2
        else:
            return 0.1
    else:  # 夏季
        if exact_time < 17.0:
            return 1.0
        elif 17.0 <= exact_time < 18.0:
            progress = exact_time - 17.0
            return 1.0 - progress * 0.05
        elif 18.0 <= exact_time < 19.0:
            progress = exact_time - 18.0
            return 0.95 - progress * 0.15
        elif 19.0 <= exact_time < 20.0:
            progress = exact_time - 19.0
            return 0.8 - progress * 0.4
        elif 20.0 <= exact_time < 21.0:
            progress = exact_time - 20.0
            return 0.4 - progress * 0.3
        else:
            return 0.1
    
    return 1.0

def load_scaler():
    """加载或创建归一化器"""
    try:
        # 尝试加载已保存的归一化参数
        mean = np.load('mypackage/process_data/models/scaler_mean.npy')
        std = np.load('mypackage/process_data/models/scaler_std.npy')
        
        scaler = StandardScaler()
        scaler.mean = mean
        scaler.std = std
        return scaler
    except FileNotFoundError:
        
        # 读取原始数据
        data_path = os.path.join(args.root_path, args.data_path)
        original_data = pd.read_csv(data_path)
        target_col = args.target
        
        if target_col in original_data.columns:
            # 计算训练集统计信息（前70%数据）
            num_train = int(len(original_data) * 0.7)
            train_power = original_data[target_col][:num_train]
            
            train_mean = train_power.mean()
            train_std = train_power.std()
            
            # 保存归一化参数
            os.makedirs('mypackage/process_data/models', exist_ok=True)
            np.save('mypackage/process_data/models/scaler_mean.npy', np.array([train_mean]))
            np.save('mypackage/process_data/models/scaler_std.npy', np.array([train_std]))
            
            # 创建StandardScaler
            scaler = StandardScaler()
            scaler.mean = np.array([train_mean])
            scaler.std = np.array([train_std])
            return scaler
        else:
            raise ValueError(f"未找到目标列 '{target_col}'")

def process_negative_values_with_smoothing(predictions, window_size=3):
    """
    使用滑动窗口均值处理负值
    """
    processed = predictions.copy()
    
    if len(predictions.shape) > 1:
        original_shape = predictions.shape
        flat_predictions = predictions.reshape(-1)
        
        for i in range(len(flat_predictions)):
            if flat_predictions[i] < 0:
                start_idx = max(0, i - window_size // 2)
                end_idx = min(len(flat_predictions), i + window_size // 2 + 1)
                
                window_values = flat_predictions[start_idx:end_idx]
                positive_values = window_values[window_values >= 0]
                
                if len(positive_values) > 0:
                    flat_predictions[i] = np.mean(positive_values)
                else:
                    flat_predictions[i] = 0.0
        
        processed = flat_predictions.reshape(original_shape)
    else:
        for i in range(len(predictions)):
            if predictions[i] < 0:
                start_idx = max(0, i - window_size // 2)
                end_idx = min(len(predictions), i + window_size // 2 + 1)
                
                window_values = predictions[start_idx:end_idx]
                positive_values = window_values[window_values >= 0]
                
                if len(positive_values) > 0:
                    processed[i] = np.mean(positive_values)
                else:
                    processed[i] = 0.0
    
    return np.maximum(processed, 0.0)

def process_solar_predictions(predictions):
    """
    处理太阳能预测结果
    - 处理负值
    - 应用太阳能特定的处理逻辑
    """
    processed = predictions.copy()
    
    # 将负值设为0
    processed = np.maximum(processed, 0.0)
    
    return processed

def sliding_window_prediction(data, window_size=96, prediction_length=24):
    print("开始太阳能发电滑动窗口预测...")
    
    # 初始化实验
    exp = Exp_Informer(args)
    
    # 添加调试信息
    print(f"args.inverse 设置为: {args.inverse}")
    print(f"exp.args.inverse 设置为: {exp.args.inverse}")
    
    # 加载归一化器
    scaler = load_scaler()
    print(f"归一化参数: mean={scaler.mean}, std={scaler.std}")
    
    # 检查模型文件是否存在
    model_name = "solar-exp_0"  # 修改为实际存在的模型名称
    setting = f'{args.model}_custom_ftM_sl{args.seq_len}_ll{args.label_len}_pl{args.pred_len}_dm{args.d_model}_nh{args.n_heads}_el{args.e_layers}_dl{args.d_layers}_df{args.d_ff}_at{args.attn}_fc{args.factor}_eb{args.embed}_dtTrue_mxTrue_{model_name}'
    model_dir = os.path.join('mypackage/process_data/Informer2020-main/Informer2020-main/checkpoints', setting)
    model_path = os.path.join(model_dir, 'checkpoint.pth')
    
    if not os.path.exists(model_path):
        print(f"模型文件不存在: {model_path}")

        return None
    
    # 加载模型
    exp.model.load_state_dict(torch.load(model_path, map_location='cpu' if not args.use_gpu else None))
    exp.model.eval()
    
    # 准备存储所有预测结果
    total_predictions_needed = days_to_predict * predictions_per_day
    all_predictions = []
    
    # 从原数据获取最后的时间点
    if 'date' in data.columns:
        last_time = pd.to_datetime(data['date'].iloc[-1])
    elif 'timestamp' in data.columns:
        last_time = pd.to_datetime(data['timestamp'].iloc[-1])
    elif 'time' in data.columns:
        last_time = pd.to_datetime(data['time'].iloc[-1])
    else:
        print("警告：未找到时间列，使用默认起始时间")
        last_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 预测从原数据最后时间点的下一个时间步开始
    start_time = last_time + timedelta(minutes=15)
    print(f"预测起始时间: {start_time.strftime('%Y-%m-%d %H:%M')}")
    
    # 执行滑动窗口预测 - 移除夜间判零逻辑，直接预测所有时间段
    for prediction_step in range(total_predictions_needed):
        # 计算当前预测时间点
        current_time = start_time + timedelta(minutes=15 * prediction_step * args.pred_len)
        current_hour = current_time.hour
        current_month = current_time.month
        
        
        # 获取预测数据
        try:
            pred_data, pred_loader = exp._get_data(flag='pred')
        except Exception as e:
            print(e)
        
        # 执行预测
        preds = []
        for i, (batch_x, batch_y, batch_x_mark, batch_y_mark) in enumerate(pred_loader):
            pred, _ = exp._process_one_batch(pred_data, batch_x, batch_y, batch_x_mark, batch_y_mark)
            preds.append(pred.detach().cpu().numpy())
        
        # 处理预测结果
        preds = np.array(preds)
        preds = preds.reshape(-1, preds.shape[-2], preds.shape[-1])
        
        # 应用平滑的日落衰减因子（仅在白天时段）
        if not is_nighttime_seasonal(current_month, current_hour):
            decay_factor = get_sunset_decay_factor_smooth(current_hour, current_time.minute, current_month)
            preds = preds * decay_factor
            print(f"  -> 时间: {current_time.strftime('%H:%M')}, 衰减因子: {decay_factor:.3f}")
        
        # 添加负值处理：使用均值平滑
        preds = process_negative_values_with_smoothing(preds, window_size=5)
        
        all_predictions.append(preds)
        

    
    # 拼接所有预测结果
    concatenated_predictions = np.concatenate([pred[:, :args.pred_len, :] for pred in all_predictions], axis=1)
    

    
    # 由于args.inverse=True，模型已经自动反归一化，直接使用预测结果
    restored_predictions = concatenated_predictions
    
    # 对整体结果再次进行均值平滑处理
    restored_predictions = process_negative_values_with_smoothing(restored_predictions, window_size=3)
    
    # 最终处理
    restored_predictions = process_solar_predictions(restored_predictions)
    
    # 保存结果
    os.makedirs('mypackage/process_data/data/output', exist_ok=True)
    # 完全移除npy文件保存
    
    # 创建带时间戳的DataFrame
    timestamps = [start_time + timedelta(minutes=15*i) for i in range(days_to_predict * steps_per_day)]
    
    # 重塑为2D数组
    reshaped = restored_predictions.reshape(-1, restored_predictions.shape[-1])
    
    # 创建DataFrame，列名改为time和power
    df_result = pd.DataFrame({
        'time': timestamps,
        'power': reshaped[:, 0]
    })
    
    # ===== 关键新增：后处理置零逻辑 =====
    print("\n=== 开始后处理置零 ===")
    zero_count = 0
    for i, row in df_result.iterrows():
        time_obj = pd.to_datetime(row['time'])
        hour = time_obj.hour
        month = time_obj.month
        
        # 根据季节性规则判断是否需要置零
        if is_nighttime_seasonal(month, hour):
            df_result.at[i, 'power'] = 0.0
            zero_count += 1
    

    
    # 只保存CSV文件 - 修改文件名为solar_output
    df_result.to_csv('mypackage/process_data/data/output/solar_output.csv', index=False)
    
    return df_result

# if __name__ == "__main__":

def solar_predict(data_path):
    # 加载太阳能数据
    # data_path = "C:\\Users\yhh\PycharmProjects\FlaskProject\mypackage\process_data\data\input\solar_input.csv"#'mypackage/process_data/data/input/solar_input.csv'

    try:
        # 读取数据
        data = pd.read_csv(data_path)
        print(f"成功加载数据，形状: {data.shape}")
        print(f"数据列: {data.columns.tolist()}")
        
        # 执行滑动窗口预测
        result = sliding_window_prediction(data)
        
        if result is not None:
            print("\n预测完成！")
            print(f"预测结果保存在: mypackage/process_data/data/output/solar_sliding_window_predictions.csv")
            return "Ok"
        else:
            print("预测失败！")
            raise Exception("Unknown Error")
            
    except FileNotFoundError:
        print(f"数据文件不存在: {data_path}")
        print("请确保数据文件路径正确！")
        raise
    except Exception as e:
        print(f"加载数据时出错: {e}")
        raise e