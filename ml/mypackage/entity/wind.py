import pandas as pd
from openai import OpenAI
import os
from datetime import datetime

# 初始化OpenAI客户端
client = OpenAI(
    api_key= "sk-cf11a6440e154985a9767e1596950656",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


def analyze_combine_data_wind(original_path, forecast_path,txt_dir):
    """分析原始风能数据与预测数据并生成决策建议"""
    # 1. 读取两文件数据，并转换格式
    df_original = pd.read_csv(original_path)
    df_original['date'] = pd.to_datetime(df_original['date'])

    df_forecast = pd.read_csv(forecast_path)
    df_forecast['time'] = pd.to_datetime(df_forecast['time'])
    df_forecast_perday = df_forecast[0:96].copy()
    df_forecast_perweek = df_forecast[0:672].copy()
    df_forecast_permonth = df_forecast[0:2880].copy()


    # 2. 关键风能指标对比

    # 计算每日平均功率
    daily_avg_power = df_forecast.groupby(df_forecast['time'].dt.date)['power'].mean()
    daily_avg_power_perday = df_forecast_perday.groupby(df_forecast_perday['time'].dt.date)['power'].mean()
    daily_avg_power_perweek = df_forecast_perweek.groupby(df_forecast_perweek['time'].dt.date)['power'].mean()
    daily_avg_power_permonth = df_forecast_permonth.groupby(df_forecast_permonth['time'].dt.date)['power'].mean()
    

    # 新的无风天气逻辑：按天计算平均功率，若低于阈值则判断为无风天气
    # 设置阴雨天气的功率阈值，单位为MW，可以根据实际情况调整
    no_wind_power_threshold = 0.4 *  df_original['power'].mean()
    no_wind_days = daily_avg_power[daily_avg_power < no_wind_power_threshold]
    no_wind_days_perday = daily_avg_power_perday[daily_avg_power_perday < no_wind_power_threshold]
    no_wind_days_perweek = daily_avg_power_perweek[daily_avg_power_perweek < no_wind_power_threshold]
    no_wind_days_permonth = daily_avg_power_permonth[daily_avg_power_permonth < no_wind_power_threshold]
    
    total_days = len(daily_avg_power)
    total_days_perday = len(daily_avg_power_perday)
    total_days_perweek = len(daily_avg_power_perweek)
    total_days_permonth = len(daily_avg_power_permonth)
    
    no_wind_probability = len(no_wind_days) / total_days * 100 if total_days > 0 else 0
    no_wind_probability_perday = len(no_wind_days_perday) / total_days_perday * 100 if total_days_perday > 0 else 0
    no_wind_probability_perweek = len(no_wind_days_perweek) / total_days_perweek * 100 if total_days_perweek > 0 else 0
    no_wind_probability_permonth = len(no_wind_days_permonth) / total_days_permonth * 100 if total_days_permonth > 0 else 0

    # 3. 计算数据
    # 计算原始数据
    comparison_general = {
        "原始数据时段": f"{df_original['date'].min()} 至 {df_original['date'].max()}",
        "10m处风速峰值": f"{df_original['Wind speed at height of 10 meters (m/s)'].max():.2f} MW",
        '10m处风速峰值时刻': f"{df_original.loc[df_original['Wind speed at height of 10 meters (m/s)'].idxmax(),'date']}",
        "10m处风速平均值": f"{df_original['Wind speed at height of 10 meters (m/s)'].mean():.2f} MW",
        "30m处风速峰值": f"{df_original['Wind speed at height of 30 meters (m/s)'].max():.2f} MW",
        '30m处风速峰值时刻': f"{df_original.loc[df_original['Wind speed at height of 30 meters (m/s)'].idxmax(),'date']}",
        "30m处风速平均值": f"{df_original['Wind speed at height of 30 meters (m/s)'].mean():.2f} MW",
        "50m处风速峰值": f"{df_original['Wind speed at height of 50 meters (m/s)'].max():.2f} MW",
        '50m处风速峰值时刻': f"{df_original.loc[df_original['Wind speed at height of 50 meters (m/s)'].idxmax(),'date']}",
        "50m处风速平均值": f"{df_original['Wind speed at height of 50 meters (m/s)'].mean():.2f} MW",
        "轮毂处风速峰值": f"{df_original['Wind speed - at the height of wheel hub (m/s)'].max():.2f} MW",
        '轮毂处风速峰值时刻': f"{df_original.loc[df_original['Wind speed - at the height of wheel hub (m/s)'].idxmax(),'date']}",
        "轮毂处风速平均值": f"{df_original['Wind speed - at the height of wheel hub (m/s)'].mean():.2f} MW",
        "最低气温": f"{df_original['Air temperature  (°C)'].min():.2f}°C",
        '最低气温时刻': f"{df_original.loc[df_original['Air temperature  (°C)'].idxmin(),'date']}",
        "最高气温": f"{df_original['Air temperature  (°C)'].max():.2f}°C",
        '最高气温时刻': f"{df_original.loc[df_original['Air temperature  (°C)'].idxmax(),'date']}",
        "气温极差": f"{df_original['Air temperature  (°C)'].max()-df_original['Air temperature  (°C)'].min():.2f}°C",
        "最低气压": f"{df_original['Atmosphere (hpa)'].min():.2f} hpa",
        '最低气压时刻': f"{df_original.loc[df_original['Atmosphere (hpa)'].idxmin(),'date']}",
        "最高气压": f"{df_original['Atmosphere (hpa)'].max():.2f} hpa",
        '最高气压时刻': f"{df_original.loc[df_original['Atmosphere (hpa)'].idxmax(),'date']}",
        "气压极差": f"{df_original['Atmosphere (hpa)'].max()-df_original['Atmosphere (hpa)'].min():.2f} hpa",
        "最低相对湿度": f"{df_original['Relative humidity (%)'].min():.2f}%",
        '最低相对湿度时刻': f"{df_original.loc[df_original['Relative humidity (%)'].idxmin(),'date']}",
        "最高相对湿度": f"{df_original['Relative humidity (%)'].max():.2f}%",
        '最高相对湿度时刻': f"{df_original.loc[df_original['Relative humidity (%)'].idxmax(),'date']}",
        "相对湿度极差": f"{df_original['Relative humidity (%)'].max()-df_original['Relative humidity (%)'].min():.2f}%",
        "峰值输出功率": f"{df_original['power'].max():.2f} MW",
        '峰值输出功率时刻': f"{df_original.loc[df_original['power'].idxmax(),'date']}",
        "平均输出功率": f"{df_original['power'].mean():.2f} MW",
    }

    # 计算每日数据
    comparison_perday = {
        "预测数据时段": f"{df_forecast_perday['time'].min()} 至 {df_forecast_perday['time'].max()}",
        "平均输出功率": f"{df_forecast_perday['power'].mean():.2f} MW",
        "峰值输出功率": f"{df_forecast_perday['power'].max():.2f} MW",
        "峰值输出功率时刻": f"{df_forecast_perday.loc[df_forecast_perday['power'].idxmax(),'time']}",
        "最高日平均功率": f"{daily_avg_power_perday.max():.2f} MW",
        "最高日平均功率时刻": f"{df_forecast_perday[df_forecast_perday['time'].dt.date == daily_avg_power_perday.idxmax()]['time'].min()}",
        "最低日平均功率": f"{daily_avg_power_perday.min():.2f} MW",
        "最低日平均功率时刻": f"{df_forecast_perday[df_forecast_perday['time'].dt.date == daily_avg_power_perday.idxmin()]['time'].min()}",
        "日平均功率极差": f"{daily_avg_power_perday.max()-daily_avg_power_perday.min():.2f} MW",
        "发电功率变化率": f"{(df_forecast_perday['power'].mean() - df_original['power'].mean()) / df_original['power'].mean():.2%}",
        "预测波动系数": f"{df_forecast_perday['power'].std() / df_forecast_perday['power'].mean():.2%}",
        "无风天气概率": f"{no_wind_probability_perday:.1f}%",
    }

    # 计算每周数据
    comparison_perweek = {
        "预测数据时段": f"{df_forecast_perweek['time'].min()} 至 {df_forecast_perweek['time'].max()}",
        "平均输出功率": f"{df_forecast_perweek['power'].mean():.2f} MW",
        "峰值输出功率": f"{df_forecast_perweek['power'].max():.2f} MW",
        "峰值输出功率时刻": f"{df_forecast_perweek.loc[df_forecast_perweek['power'].idxmax(),'time']}",
        "最高日平均功率": f"{daily_avg_power_perweek.max():.2f} MW",
        "最高日平均功率时刻": f"{df_forecast_perweek[df_forecast_perweek['time'].dt.date == daily_avg_power_perweek.idxmax()]['time'].min()}",
        "最低日平均功率": f"{daily_avg_power_perweek.min():.2f} MW",
        "最低日平均功率时刻": f"{df_forecast_perweek[df_forecast_perweek['time'].dt.date == daily_avg_power_perweek.idxmin()]['time'].min()}",
        "日平均功率极差": f"{daily_avg_power_perweek.max()-daily_avg_power_perweek.min():.2f} MW",
        "发电功率变化率": f"{(df_forecast_perweek['power'].mean() - df_original['power'].mean()) / df_original['power'].mean():.2%}",
        "预测波动系数": f"{df_forecast_perweek['power'].std() / df_forecast_perweek['power'].mean():.2%}",
        "无风天气概率": f"{no_wind_probability_perweek:.1f}%",
    }

    # 计算每月数据
    comparison_permonth = {
        "预测数据时段": f"{df_forecast_permonth['time'].min()} 至 {df_forecast_permonth['time'].max()}",
        "平均输出功率": f"{df_forecast_permonth['power'].mean():.2f} MW",
        "峰值输出功率": f"{df_forecast_permonth['power'].max():.2f} MW",
        "峰值输出功率时刻": f"{df_forecast_permonth.loc[df_forecast_permonth['power'].idxmax(),'time']}",
        "最高日平均功率": f"{daily_avg_power_permonth.max():.2f} MW",
        "最高日平均功率时刻": f"{df_forecast_permonth[df_forecast_permonth['time'].dt.date == daily_avg_power_permonth.idxmax()]['time'].min()}",
        "最低日平均功率": f"{daily_avg_power_permonth.min():.2f} MW",
        "最低日平均功率时刻": f"{df_forecast_permonth[df_forecast_permonth['time'].dt.date == daily_avg_power_permonth.idxmin()]['time'].min()}",
        "日平均功率极差": f"{daily_avg_power_permonth.max()-daily_avg_power_permonth.min():.2f} MW",
        "发电功率变化率": f"{(df_forecast_permonth['power'].mean() - df_original['power'].mean()) / df_original['power'].mean():.2%}",
        "预测波动系数": f"{df_forecast_permonth['power'].std() / df_forecast_permonth['power'].mean():.2%}",
        "无风天气概率": f"{no_wind_probability_permonth:.1f}%",
    }

    # 计算全部数据
    comparison = {
        "预测数据时段": f"{df_forecast['time'].min()} 至 {df_forecast['time'].max()}",
        "平均输出功率": f"{df_forecast['power'].mean():.2f} MW",
        "峰值输出功率": f"{df_forecast['power'].max():.2f} MW",
        "峰值输出功率时刻": f"{df_forecast.loc[df_forecast['power'].idxmax(),'time']}",
        "最高日平均功率": f"{daily_avg_power.max():.2f} MW",
        "最高日平均功率时刻": f"{df_forecast[df_forecast['time'].dt.date == daily_avg_power.idxmax()]['time'].min()}",
        "最低日平均功率": f"{daily_avg_power.min():.2f} MW",
        "最低日平均功率时刻": f"{df_forecast[df_forecast['time'].dt.date == daily_avg_power.idxmin()]['time'].min()}",
        "日平均功率极差": f"{daily_avg_power.max()-daily_avg_power.min():.2f} MW",
        "发电功率变化率": f"{(df_forecast['power'].mean() - df_original['power'].mean()) / df_original['power'].mean():.2%}",
        "预测波动系数": f"{df_forecast['power'].std() / df_forecast['power'].mean():.2%}",
        "无风天气概率": f"{no_wind_probability:.1f}%",
    }

    # 5. 构建大模型请求prompt（太阳能场景优化）
    prompt = f"""
    以下是太阳能发电历史数据与预测数据的对比分析，请结合数据给出三个优化太阳能利用效率的决策建议：

    [原始数据]
    - 原始数据时段：{comparison_general['原始数据时段']}
    - 10m处风速峰值：{comparison_general['10m处风速峰值']}
    - 30m处风速峰值：{comparison_general['30m处风速峰值']}
    - 50m处风速峰值：{comparison_general['50m处风速峰值']}
    - 轮毂处风速峰值：{comparison_general['轮毂处风速峰值']}
    - 最低气温：{comparison_general['最低气温']}
    - 最高气温：{comparison_general['最高气温']}
    - 气温极差：{comparison_general['气温极差']}
    - 最低气压：{comparison_general['最低气压']}
    - 最高气压：{comparison_general['最高气压']}
    - 气压极差：{comparison_general['气压极差']}
    - 最低相对湿度：{comparison_general['最低相对湿度']}
    - 最高相对湿度：{comparison_general['最高相对湿度']}
    - 相对湿度极差：{comparison_general['相对湿度极差']}
    - 峰值输出功率：{comparison_general['峰值输出功率']}
    - 平均输出功率：{comparison_general['平均输出功率']}

    [预测未来一日数据]
    - 预测数据时段：{comparison_perday['预测数据时段']}
    - 峰值输出功率：{comparison_perday['峰值输出功率']}
    - 最高日平均功率：{comparison_perday['最高日平均功率']}
    - 最低日平均功率：{comparison_perday['最低日平均功率']}
    - 日平均功率极差：{comparison_perday['日平均功率极差']}
    - 发电功率变化率：{comparison_perday['发电功率变化率']}
    - 预测波动系数：{comparison_perday['预测波动系数']}
    - 无风天气概率：{comparison_perday['无风天气概率']}

    [预测未来一周数据]
    - 预测数据时段：{comparison_perweek['预测数据时段']}
    - 峰值输出功率：{comparison_perweek['峰值输出功率']}
    - 最高日平均功率：{comparison_perweek['最高日平均功率']}
    - 最低日平均功率：{comparison_perweek['最低日平均功率']}
    - 日平均功率极差：{comparison_perweek['日平均功率极差']}
    - 发电功率变化率：{comparison_perweek['发电功率变化率']}
    - 预测波动系数：{comparison_perweek['预测波动系数']}
    - 无风天气概率：{comparison_perweek['无风天气概率']}

    [预测未来一月数据]
    - 预测数据时段：{comparison_permonth['预测数据时段']}
    - 峰值输出功率：{comparison_permonth['峰值输出功率']}
    - 最高日平均功率：{comparison_permonth['最高日平均功率']}
    - 最低日平均功率：{comparison_permonth['最低日平均功率']}
    - 日平均功率极差：{comparison_permonth['日平均功率极差']}
    - 发电功率变化率：{comparison_permonth['发电功率变化率']}
    - 预测波动系数：{comparison_permonth['预测波动系数']}
    - 无风天气概率：{comparison_permonth['无风天气概率']}

    [预测未来一季度数据]
    - 预测数据时段：{comparison['预测数据时段']}
    - 峰值输出功率：{comparison['峰值输出功率']}
    - 最高日平均功率：{comparison['最高日平均功率']}
    - 最低日平均功率：{comparison['最低日平均功率']}
    - 日平均功率极差：{comparison['日平均功率极差']}
    - 发电功率变化率：{comparison['发电功率变化率']}
    - 预测波动系数：{comparison['预测波动系数']}
    - 无风天气概率：{comparison['无风天气概率']}

    [决策要求]
    1. 作为一名专业的风能发电决策助手，请根据提供的数据对比，提出3项优化风能利用的具体措施，按照综合评级星级从高到低输出文本，数据场景为城市风能发电系统。
    2. 每项措施需严格按照以下结构输出：
        - 决策建议X：[措施名称]
        - 一、决策背景与核心目标：结合数据说明为何提出此措施，解决什么问题。
        - 二、实施路径与操作细节：分步骤说明如何实施，包括目标群体、具体操作方法、技术支撑等。
        - 三、风险应对与保障措施：识别可能的风险并提出解决方案。
        - 四、长期价值与可持续性：说明措施的长期效益和可扩展性。
        - 五、决策落地建议：提出具体的实施步骤和优先级。
        - 六、综合评估：
        *[星级]*经济性：说明成本效益比，给出星级并简要解释原因。
        *[星级]*可持续性：评估措施的长期适用性和可复制性，给出星级并简要解释原因。
        *[星级]*实施难度：分析实施过程中的障碍和挑战，给出星级并简要解释原因。
        *[星级]*综合评级：根据前三项给出综合评分，说明该措施的核心优势。
    3. 输出内容需严格使用中文，确保专业术语准确规范。
    4. 优先考虑可在预测时段前快速落地的方案，同时兼顾长期效益。
    5. 经济性、可持续性、综合评级星级越高说明决策效果更好，实施难度星级越高代表实施难度越高与决策效果越差，按照综合评级从高到低排列各项措施后再进行输出决策内容。
    6. 在两个决策内容之间，添加一个空行输入三个///作为分割，最后一个决策内容输出结束后无需输入三个///分割。
    7. 输出文本时不应使用markdown格式，除了*[星级]*处可出现*，其他地方不允许输出*，严格按照模板输出纯文本。
    8. 在每个决策内容输出结束后，输出一个空行，再输出（注：以上措施仅供参考，实际落地需结合本地电网结构、政策环境等要素进行适应性调整）。
    9. 决策内容中不要出现'>''<''≥''≤'，使用大于、小于、大于等于、小于等于替代。
    10. 输出每个决策时参考《》中的模板进行输出。

    《
    决策建议1：动态偏航控制系统升级  
    一、决策背景与核心目标  
    历史数据显示轮毂处风速峰值（30.25MW）未被充分利用（平均输出功率仅23.87MW），预测未来一周/月的波动系数高达113.08%-124.98%，且无风天气概率达28.6%-42.4%。通过部署动态偏航控制系统，实时调整风力机朝向与叶片角度，提升低风速段的能量捕获效率，目标将日均功率提升10%-15%。  

    二、实施路径与操作细节  
    1. 系统升级方案  
    目标群体：现有单机容量大于等于2MW的风力发电机组。  
    技术方案：  
    （1）安装高精度激光雷达测风仪：在轮毂前50米处部署，提前20秒预判风速与风向变化。  
    （2）集成自适应控制算法：基于历史风速分布数据（如30m处峰值29.19MW）训练AI模型，优化偏航响应策略。  
    （3）改造传动系统：采用模块化齿轮箱，支持±5°动态偏航调节，调节周期缩短至30秒/次。  
    2. 实施阶段  
    （1）数据建模阶段（预测时段前7天）：  
    利用SCADA系统导出近1年偏航数据，识别低效运行时段（如风速8-12m/s时偏航延迟大于60秒）。  
    （2）硬件改造阶段（预测时段前3天）：  
    优先改造位于风速梯度显著区域（50m与轮毂处风速差大于1.5m/s）的机组。  
    （3）算法优化阶段：  
    每6小时更新一次控制参数，通过数字孪生平台模拟验证调整效果。  

    三、风险应对与保障措施  
    1. 机械磨损风险：  
    在齿轮箱加装振动监测传感器，设定磨损阈值（振动幅度大于0.8mm时自动锁定）。  
    2. 极端气候风险：  
    当气温低于-15°C时，启动加热型润滑系统防止液压油冻结。  

    四、长期价值与可持续性  
    1. 适应性提升：可兼容未来15MW级海上风机技术标准。  
    2. 数据资产积累：持续优化AI模型，预测精度每季度提升2%-3%。  

    五、决策落地建议  
    1. 优先改造近3年投运的新机组（兼容性更佳）。  
    2. 申请工业技改专项补贴（部分省份可覆盖20%成本）。  
    3. 建立偏航效率KPI考核机制，将动态调节响应时间纳入运维指标。

    六、综合评估  
    *4*经济性：改造成本约8万元/机组，投资回收期2.3年（按提升12%发电量计算）。  
    *5*可持续性：降低机组空转损耗，延长关键部件寿命20%以上。  
    *3*实施难度：需同步升级数据采集系统与控制系统。  
    *4*综合评级：兼具短期见效与长期增益的技改方案。

    （注：以上措施仅供参考，实际落地需结合本地电网结构、政策环境等要素进行适应性调整。）  
    """

    # 6. 调用大模型生成建议
    completion = client.chat.completions.create(
        model="deepseek-r1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=5000
    )
    decision = completion.choices[0].message.content.strip()

    # 6. 保存结果
    base_name = os.path.basename(os.path.splitext(original_path)[0])
    output_path = txt_dir # 此处修改txt文件名
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"{'原始数据时段'}:  {comparison_general['原始数据时段']}\n")
        f.write(f"{'十米处风速峰值'}:  {comparison_general['10m处风速峰值时刻']} {comparison_general['10m处风速峰值']}\n")
        f.write(f"{'十米处风速平均值'}:  {comparison_general['10m处风速平均值']}\n")
        f.write(f"{'三十米处风速峰值'}:  {comparison_general['30m处风速峰值时刻']} {comparison_general['30m处风速峰值']}\n")
        f.write(f"{'三十米处风速平均值'}:  {comparison_general['30m处风速平均值']}\n")
        f.write(f"{'五十米处风速峰值'}:  {comparison_general['50m处风速峰值时刻']} {comparison_general['50m处风速峰值']}\n")
        f.write(f"{'五十米处风速平均值'}:  {comparison_general['50m处风速平均值']}\n")
        f.write(f"{'轮毂处风速峰值'}:  {comparison_general['轮毂处风速峰值时刻']} {comparison_general['轮毂处风速峰值']}\n")
        f.write(f"{'轮毂处风速平均值'}:  {comparison_general['轮毂处风速平均值']}\n")
        f.write(f"{'最低气温'}:  {comparison_general['最低气温时刻']} {comparison_general['最低气温']}\n")
        f.write(f"{'最高气温'}:  {comparison_general['最高气温时刻']} {comparison_general['最高气温']}\n")
        f.write(f"{'气温极差'}:  {comparison_general['气温极差']}\n")
        f.write(f"{'最低气压'}:  {comparison_general['最低气压时刻']} {comparison_general['最低气压']}\n")
        f.write(f"{'最高气压'}:  {comparison_general['最高气压时刻']} {comparison_general['最高气压']}\n")
        f.write(f"{'气压极差'}:  {comparison_general['气压极差']}\n")
        f.write(f"{'最低相对湿度'}:  {comparison_general['最低相对湿度时刻']} {comparison_general['最低相对湿度']}\n")
        f.write(f"{'最高相对湿度'}:  {comparison_general['最高相对湿度时刻']} {comparison_general['最高相对湿度']}\n")
        f.write(f"{'相对湿度极差'}:  {comparison_general['相对湿度极差']}\n")
        f.write(f"{'峰值输出功率'}:  {comparison_general['峰值输出功率时刻']} {comparison_general['峰值输出功率']}\n")
        f.write(f"{'平均输出功率'}:  {comparison_general['平均输出功率']}\n")
        f.write("\n------\n\n")
        f.write(f"{'预测数据时段'}:  {comparison_perday['预测数据时段']}\n")
        f.write(f"{'峰值输出功率'}:  {comparison_perday['峰值输出功率时刻']} {comparison_perday['峰值输出功率']}\n")
        f.write(f"{'最高日平均功率'}:  {comparison_perday['最高日平均功率时刻']} {comparison_perday['最高日平均功率']}\n")
        f.write(f"{'最低日平均功率'}:  {comparison_perday['最低日平均功率时刻']} {comparison_perday['最低日平均功率']}\n")
        f.write(f"{'日平均功率极差'}:  {comparison_perday['日平均功率极差']}\n")
        f.write(f"{'发电功率变化率'}:  {comparison_perday['发电功率变化率']}\n")
        f.write(f"{'预测波动系数'}:  {comparison_perday['预测波动系数']}\n")
        f.write(f"{'无风天气概率'}:  {comparison_perday['无风天气概率']}\n")
        f.write("\n///\n\n")
        f.write(f"{'预测数据时段'}:  {comparison_perweek['预测数据时段']}\n")
        f.write(f"{'峰值输出功率'}:  {comparison_perweek['峰值输出功率时刻']} {comparison_perweek['峰值输出功率']}\n")
        f.write(f"{'最高日平均功率'}:  {comparison_perweek['最高日平均功率时刻']} {comparison_perweek['最高日平均功率']}\n")
        f.write(f"{'最低日平均功率'}:  {comparison_perweek['最低日平均功率时刻']} {comparison_perweek['最低日平均功率']}\n")
        f.write(f"{'日平均功率极差'}:  {comparison_perweek['日平均功率极差']}\n")
        f.write(f"{'发电功率变化率'}:  {comparison_perweek['发电功率变化率']}\n")
        f.write(f"{'预测波动系数'}:  {comparison_perweek['预测波动系数']}\n")
        f.write(f"{'无风天气概率'}:  {comparison_perweek['无风天气概率']}\n")
        f.write("\n///\n\n")
        f.write(f"{'预测数据时段'}:  {comparison_permonth['预测数据时段']}\n")
        f.write(f"{'峰值输出功率'}:  {comparison_permonth['峰值输出功率时刻']} {comparison_permonth['峰值输出功率']}\n")
        f.write(f"{'最高日平均功率'}:  {comparison_permonth['最高日平均功率时刻']} {comparison_permonth['最高日平均功率']}\n")
        f.write(f"{'最低日平均功率'}:  {comparison_permonth['最低日平均功率时刻']} {comparison_permonth['最低日平均功率']}\n")
        f.write(f"{'日平均功率极差'}:  {comparison_permonth['日平均功率极差']}\n")
        f.write(f"{'发电功率变化率'}:  {comparison_permonth['发电功率变化率']}\n")
        f.write(f"{'预测波动系数'}:  {comparison_permonth['预测波动系数']}\n")
        f.write(f"{'无风天气概率'}:  {comparison_permonth['无风天气概率']}\n")
        f.write("\n///\n\n")
        f.write(f"{'预测数据时段'}:  {comparison['预测数据时段']}\n")
        f.write(f"{'峰值输出功率'}:  {comparison['峰值输出功率时刻']} {comparison['峰值输出功率']}\n")
        f.write(f"{'最高日平均功率'}:  {comparison['最高日平均功率时刻']} {comparison['最高日平均功率']}\n")
        f.write(f"{'最低日平均功率'}:  {comparison['最低日平均功率时刻']} {comparison['最低日平均功率']}\n")
        f.write(f"{'日平均功率极差'}:  {comparison['日平均功率极差']}\n")
        f.write(f"{'发电功率变化率'}:  {comparison['发电功率变化率']}\n")
        f.write(f"{'预测波动系数'}:  {comparison['预测波动系数']}\n")
        f.write(f"{'无风天气概率'}:  {comparison['无风天气概率']}\n")
        f.write("\n------\n\n")
        f.write(decision)
    print(f"结果已保存至 {output_path}")


if __name__ == "__main__":
    original_csv = 'wind/original_data/wind1.csv' # 此处修改原始数据地址
    forecast_csv = 'wind/forecast_data/wind2.csv' # 此处修改预测数据地址
    txt_dir = 'wind/txt' # 此处修改txt文件目录
    analyze_combine_data_wind(original_csv, forecast_csv,txt_dir)