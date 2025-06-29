import numpy as np
import pandas as pd
import torch
import sys
import os
import argparse
from datetime import datetime, timedelta

# 添加Informer项目路径
sys.path.append(r'C:\yinxingguo\Informer2020-main\Informer2020-main')
from exp.exp_informer import Exp_Informer
from utils.tools import StandardScaler

# 参数设置
parser = argparse.ArgumentParser(description='风电功率Informer滑动窗口预测')
parser.add_argument('--model', type=str, default='informer', help='模型类型')
parser.add_argument('--data', type=str, default='custom', help='数据集名称')
parser.add_argument('--root_path', type=str, default='mypackage/process_data/data/input', help='数据根目录')
parser.add_argument('--data_path', type=str, default='wind_input.csv', help='数据文件')
parser.add_argument('--features', type=str, default='S', help='预测任务类型')
parser.add_argument('--target', type=str, default='power', help='目标特征')
parser.add_argument('--freq', type=str, default='h', help='时间频率，h表示小时级(hour)')
parser.add_argument('--checkpoints', type=str, default='mypackage/process_data/checkpoints/', help='模型检查点位置')
parser.add_argument('--seq_len', type=int, default=96, help='输入序列长度')
parser.add_argument('--label_len', type=int, default=48, help='标签序列长度')
parser.add_argument('--pred_len', type=int, default=24, help='预测序列长度，24表示6小时(15分钟×24=6小时)')
parser.add_argument('--enc_in', type=int, default=1, help='编码器输入大小 - 1个特征')
parser.add_argument('--dec_in', type=int, default=1, help='解码器输入大小 - 1个特征')
parser.add_argument('--c_out', type=int, default=1, help='输出大小')
parser.add_argument('--d_model', type=int, default=512, help='模型维度')
parser.add_argument('--n_heads', type=int, default=8, help='注意力头数')
parser.add_argument('--e_layers', type=int, default=3, help='编码器层数')
parser.add_argument('--d_layers', type=int, default=2, help='解码器层数')
parser.add_argument('--d_ff', type=int, default=2048, help='前馈网络维度')
parser.add_argument('--factor', type=int, default=5, help='ProbSparse注意力因子')
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
# 修改第52行的参数设置
parser.add_argument('--inverse', type=bool, default=True, help='是否反转转换，用于还原预测值到原始范围')
# 或者更简单的方式，直接在代码中强制设置
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

def load_scaler():
    """加载或创建归一化器"""
    try:
        # 尝试加载已保存的归一化参数
        mean = np.load('mypackage/process_data/models/scaler_mean_wind.npy')
        std = np.load('mypackage/process_data/models/scaler_std_wind.npy')
        
        scaler = StandardScaler()
        scaler.mean = mean
        scaler.std = std
        return scaler
    except FileNotFoundError:
        print("未找到归一化参数文件，从原始数据计算...")
        
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
            np.save('mypackage/process_data/models/scaler_mean_wind.npy', np.array([train_mean]))
            np.save('mypackage/process_data/models/scaler_std_wind.npy', np.array([train_std]))
            
            # 创建StandardScaler
            scaler = StandardScaler()
            scaler.mean = np.array([train_mean])
            scaler.std = np.array([train_std])
            return scaler
        else:
            raise ValueError(f"未找到目标列 '{target_col}'")

def process_wind_predictions(predictions, wind_speed_threshold=2.0):
    """
    处理风电预测结果
    - 处理负值
    - 应用风速阈值（低风速时功率接近0）
    """
    processed = predictions.copy()
    
    # 将负值设为0
    processed = np.maximum(processed, 0.0)
    
    
    return processed

def sliding_window_prediction(data, window_size=96, prediction_length=24):
    print("开始风电功率滑动窗口预测...")
    # 初始化实验
    exp = Exp_Informer(args)
    

    
    # 加载归一化器
    scaler = load_scaler()

    
    # 检查模型文件是否存在
    model_name = "clean-power-univariate-v1_0"
    setting = f'{args.model}_custom_ftS_sl{args.seq_len}_ll{args.label_len}_pl{args.pred_len}_dm{args.d_model}_nh{args.n_heads}_el{args.e_layers}_dl{args.d_layers}_df{args.d_ff}_at{args.attn}_fc{args.factor}_eb{args.embed}_dtTrue_mxTrue_{model_name}'
    model_dir = os.path.join('mypackage/process_data/models/checkpoints', setting)
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
    # 假设数据中有时间列，需要根据实际列名调整
    if 'date' in data.columns:
        last_time = pd.to_datetime(data['date'].iloc[-1])
    elif 'timestamp' in data.columns:
        last_time = pd.to_datetime(data['timestamp'].iloc[-1])
    elif 'time' in data.columns:
        last_time = pd.to_datetime(data['time'].iloc[-1])
    else:
        # 如果没有时间列，使用默认起始时间
        print("警告：未找到时间列，使用默认起始时间")
        last_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 预测从原数据最后时间点的下一个时间步开始
    start_time = last_time + timedelta(minutes=15)
    print(f"预测起始时间: {start_time.strftime('%Y-%m-%d %H:%M')}")
    
    # 执行滑动窗口预测
    for prediction_step in range(total_predictions_needed):
        # 计算当前预测时间点
        current_time = start_time + timedelta(minutes=15 * prediction_step * args.pred_len)
        
        print(f"预测第 {prediction_step+1}/{total_predictions_needed} 批次 (时间: {current_time.strftime('%Y-%m-%d %H:%M')})...")
        
        # 获取预测数据
        pred_data, pred_loader = exp._get_data(flag='pred')
        
        # 执行预测
        preds = []
        for i, (batch_x, batch_y, batch_x_mark, batch_y_mark) in enumerate(pred_loader):
            pred, _ = exp._process_one_batch(pred_data, batch_x, batch_y, batch_x_mark, batch_y_mark)
            preds.append(pred.detach().cpu().numpy())
        
        # 处理预测结果
        preds = np.array(preds)
        preds = preds.reshape(-1, preds.shape[-2], preds.shape[-1])
        
        all_predictions.append(preds)
        
        print(f"  -> 预测完成，平均功率: {preds.mean():.2f}")
    
    # 拼接所有预测结果
    concatenated_predictions = np.concatenate([pred[:, :args.pred_len, :] for pred in all_predictions], axis=1)
    
    # 检查预测结果是否已经反归一化
    print(f"\n=== 预测结果检查 ===")
    print(f"预测结果统计: Mean={concatenated_predictions.mean():.2f}, Std={concatenated_predictions.std():.2f}")
    print(f"预测结果范围: {concatenated_predictions.min():.2f} - {concatenated_predictions.max():.2f}")
    print(f"args.inverse = {args.inverse}")
    

    restored_predictions = concatenated_predictions
    
    # 最终处理
    restored_predictions = process_wind_predictions(restored_predictions)
    
    # 保存结果
    os.makedirs('mypackage/process_data/data/output', exist_ok=True)
    # 完全移除npy文件保存
    
    # 创建带时间戳的DataFrame
    timestamps = [start_time + timedelta(minutes=15*i) for i in range(days_to_predict * steps_per_day)]
    
    # 重塑为2D数组
    reshaped = restored_predictions.reshape(-1, restored_predictions.shape[-1])
    
    # 创建DataFrame
    df_result = pd.DataFrame({
        'time': timestamps,
        'power': reshaped[:, 0]
    })
    
    # 只保存CSV文件 - 修改文件名为wind_output
    df_result.to_csv('mypackage/process_data/data/output/wind_output.csv', index=False)
    print(f"风电滑动窗口预测完成，结果已保存到 mypackage/process_data/data/output/wind_output.csv")
    

    
    return df_result

# if __name__ == "__main__":
def wind_predict(data_path):
    # 加载风电数据
    # data_path = 'mypackage/process_data/data/input/wind_input.csv'
    
    try:
        # 读取数据
        data = pd.read_csv(data_path)
        print(f"成功加载数据，形状: {data.shape}")
        print(f"数据列: {data.columns.tolist()}")
        
        # 执行滑动窗口预测
        result = sliding_window_prediction(data)
        
        if result is not None:
            print("\n预测完成！")
            print(f"预测结果保存在: mypackage/process_data/data/output/wind_output.csv")
            return "Ok"
        else:
            print("预测失败！")
            raise Exception("Error!")
            
    except FileNotFoundError:
        print(f"数据文件不存在: {data_path}")
        print("请确保数据文件路径正确！")
        raise
    except Exception as e:
        print(f"加载数据时出错: {e}")
        raise e