import pandas as pd
from openai import OpenAI
# import dashscope
import os
from datetime import datetime

# 初始化OpenAI客户端
client = OpenAI(
    api_key= "sk-cf11a6440e154985a9767e1596950656",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


def analyze_combine_data_solar(original_path, forecast_path, output_dir):
    """分析原始太阳能数据与预测数据并生成决策建议"""
    # 1. 读取两文件数据，并转换格式
    df_original = pd.read_csv(original_path)
    df_original['date'] = pd.to_datetime(df_original['date'])

    df_forecast = pd.read_csv(forecast_path)
    df_forecast['time'] = pd.to_datetime(df_forecast['time'])
    df_forecast_perday = df_forecast[0:96].copy()
    df_forecast_perweek = df_forecast[0:672].copy()
    df_forecast_permonth = df_forecast[0:2880].copy()


    # 2. 关键太阳能指标对比
    # 计算日照时段（简化：功率>0的时段）
    forecast_sun_hours = df_forecast[df_forecast['power'] > 0]['time'].dt.hour.unique()
    forecast_sun_hours_perday = df_forecast_perday.loc[df_forecast_perday['power'] > 0]['time'].dt.hour.unique()
    forecast_sun_hours_perweek = df_forecast_perweek.loc[df_forecast_perweek['power'] > 0]['time'].dt.hour.unique()
    forecast_sun_hours_permonth = df_forecast_permonth.loc[df_forecast_permonth['power'] > 0]['time'].dt.hour.unique()

    # 计算每日平均功率
    daily_avg_power = df_forecast.groupby(df_forecast['time'].dt.date)['power'].mean()
    daily_avg_power_perday = df_forecast_perday.groupby(df_forecast_perday['time'].dt.date)['power'].mean()
    daily_avg_power_perweek = df_forecast_perweek.groupby(df_forecast_perweek['time'].dt.date)['power'].mean()
    daily_avg_power_permonth = df_forecast_permonth.groupby(df_forecast_permonth['time'].dt.date)['power'].mean()


    # 新的阴雨天气逻辑：按天计算平均功率，若低于阈值则判断为阴雨天气
    daily_avg_power = df_forecast.groupby(df_forecast['time'].dt.date)['power'].mean()
    daily_avg_power_perday = df_forecast_perday.groupby(df_forecast_perday['time'].dt.date)['power'].mean()
    daily_avg_power_perweek = df_forecast_perweek.groupby(df_forecast_perweek['time'].dt.date)['power'].mean()
    daily_avg_power_permonth = df_forecast_permonth.groupby(df_forecast_permonth['time'].dt.date)['power'].mean()
    # 设置阴雨天气的功率阈值，单位为MW，可以根据实际情况调整
    rainy_power_threshold = 0.4 *  df_original['power'].mean()
    rainy_days = daily_avg_power[daily_avg_power < rainy_power_threshold]
    rainy_days_perday = daily_avg_power_perday[daily_avg_power_perday < rainy_power_threshold]
    rainy_days_perweek = daily_avg_power_perweek[daily_avg_power_perweek < rainy_power_threshold]
    rainy_days_permonth = daily_avg_power_permonth[daily_avg_power_permonth < rainy_power_threshold]

    total_days = len(daily_avg_power)
    total_days_perday = len(daily_avg_power_perday)
    total_days_perweek = len(daily_avg_power_perweek)
    total_days_permonth = len(daily_avg_power_permonth)

    rainy_probability = len(rainy_days) / total_days * 100 if total_days > 0 else 0
    rainy_probability_perday = len(rainy_days_perday) / total_days_perday * 100 if total_days_perday > 0 else 0
    rainy_probability_perweek = len(rainy_days_perweek) / total_days_perweek * 100 if total_days_perweek > 0 else 0
    rainy_probability_permonth = len(rainy_days_permonth) / total_days_permonth * 100 if total_days_permonth > 0 else 0

    # 3. 计算数据
    # 计算原始数据
    comparison_general = {
        "原始数据时段": f"{df_original['date'].min()} 至 {df_original['date'].max()}",
        '总太阳能辐照度峰值': f"{df_original['Total solar irradiance (W/m2)'].max():.2f} W/m2",
        '总太阳能辐照度峰值时刻': f"{df_original.loc[df_original['Total solar irradiance (W/m2)'].idxmax(),'date']}",
        "直射辐照度峰值": f"{df_original['Direct normal irradiance (W/m2)'].max():.2f} W/m2",
        '直射辐照度峰值时刻': f"{df_original.loc[df_original['Direct normal irradiance (W/m2)'].idxmax(),'date']}",
        "最低气温": f"{df_original['Air temperature  (°C) '].min():.2f}°C",
        '最低气温时刻': f"{df_original.loc[df_original['Air temperature  (°C) '].idxmin(),'date']}",
        "最高气温": f"{df_original['Air temperature  (°C) '].max():.2f}°C",
        '最高气温时刻': f"{df_original.loc[df_original['Air temperature  (°C) '].idxmax(),'date']}",
        "气温极差": f"{df_original['Air temperature  (°C) '].max()-df_original['Air temperature  (°C) '].min():.2f}°C",
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
        "预测日照时段": f"{min(forecast_sun_hours_perday)}-{max(forecast_sun_hours_perday)}点",
        "预测波动系数": f"{df_forecast_perday['power'].std() / df_forecast_perday['power'].mean():.2%}",
        "阴雨天气概率": f"{rainy_probability_perday:.1f}%",
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
        "预测日照时段": f"{min(forecast_sun_hours_perweek)}-{max(forecast_sun_hours_perweek)}点",
        "预测波动系数": f"{df_forecast_perweek['power'].std() / df_forecast_perweek['power'].mean():.2%}",
        "阴雨天气概率": f"{rainy_probability_perweek:.1f}%",
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
        "预测日照时段": f"{min(forecast_sun_hours_permonth)}-{max(forecast_sun_hours_permonth)}点",
        "预测波动系数": f"{df_forecast_permonth['power'].std() / df_forecast_permonth['power'].mean():.2%}",
        "阴雨天气概率": f"{rainy_probability_permonth:.1f}%",
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
        "预测日照时段": f"{min(forecast_sun_hours)}-{max(forecast_sun_hours)}点",
        "预测波动系数": f"{df_forecast['power'].std() / df_forecast['power'].mean():.2%}",
        "阴雨天气概率": f"{rainy_probability:.1f}%",
    }
    # 4. 构建大模型请求prompt
    prompt = f"""
    以下是太阳能发电历史数据与预测数据的对比分析，请结合数据给出三个优化太阳能利用效率的决策建议：

    [原始数据]
    - 原始数据时段：{comparison_general['原始数据时段']}
    - 总太阳能辐照度峰值：{comparison_general['总太阳能辐照度峰值']}
    - 最低气温：{comparison_general['最低气温']}
    - 最高气温：{comparison_general['最高气温']}
    - 气温极差：{comparison_general['气温极差']}
    - 最低气压：{comparison_general['最低气压']}
    - 最高气压：{comparison_general['最高气压']}
    - 气压极差：{comparison_general['气压极差']}
    - 最低相对湿度：{comparison_general['最低相对湿度']}
    - 最高相对湿度：{comparison_general['最高相对湿度']}
    - 相对湿度极差：{comparison_general['相对湿度极差']}
    - 直射辐照度峰值：{comparison_general['直射辐照度峰值']}
    - 峰值输出功率：{comparison_general['峰值输出功率']}
    - 平均输出功率：{comparison_general['平均输出功率']}

    [预测未来一日数据]
    - 预测数据时段：{comparison_perday['预测数据时段']}
    - 峰值输出功率：{comparison_perday['峰值输出功率']}
    - 最高日平均功率：{comparison_perday['最高日平均功率']}
    - 最低日平均功率：{comparison_perday['最低日平均功率']}
    - 日平均功率极差：{comparison_perday['日平均功率极差']}
    - 预测日照时段：{comparison_perday['预测日照时段']}
    - 预测波动系数：{comparison_perday['预测波动系数']}
    - 阴雨天气概率：{comparison_perday['阴雨天气概率']}

    [预测未来一周数据]
    - 预测数据时段：{comparison_perweek['预测数据时段']}
    - 峰值输出功率：{comparison_perweek['峰值输出功率']}
    - 最高日平均功率：{comparison_perweek['最高日平均功率']}
    - 最低日平均功率：{comparison_perweek['最低日平均功率']}
    - 日平均功率极差：{comparison_perweek['日平均功率极差']}
    - 预测日照时段：{comparison_perweek['预测日照时段']}
    - 预测波动系数：{comparison_perweek['预测波动系数']}
    - 阴雨天气概率：{comparison_perweek['阴雨天气概率']}

    [预测未来一月数据]
    - 预测数据时段：{comparison_permonth['预测数据时段']}
    - 峰值输出功率：{comparison_permonth['峰值输出功率']}
    - 最高日平均功率：{comparison_permonth['最高日平均功率']}
    - 最低日平均功率：{comparison_permonth['最低日平均功率']}
    - 日平均功率极差：{comparison_permonth['日平均功率极差']}
    - 预测日照时段：{comparison_permonth['预测日照时段']}
    - 预测波动系数：{comparison_permonth['预测波动系数']}
    - 阴雨天气概率：{comparison_permonth['阴雨天气概率']}

    [预测未来一季度数据]
    - 预测数据时段：{comparison['预测数据时段']}
    - 峰值输出功率：{comparison['峰值输出功率']}
    - 最高日平均功率：{comparison['最高日平均功率']}
    - 最低日平均功率：{comparison['最低日平均功率']}
    - 日平均功率极差：{comparison['日平均功率极差']}
    - 预测日照时段：{comparison['预测日照时段']}
    - 预测波动系数：{comparison['预测波动系数']}
    - 阴雨天气概率：{comparison['阴雨天气概率']}

    [决策要求]
    1. 作为一名专业的太阳能发电决策助手，请根据提供的数据对比，提出3项优化太阳能利用的具体措施，按照综合评级星级从高到低输出文本，数据场景为城市太阳能发电系统（包括分布式屋顶光伏和集中式光伏电站）。
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
    决策建议1：智能光伏追踪系统优化
    一、决策背景与核心目标
    预测数据显示，日照时段将从10-16点缩短至9-15点，峰值功率略有下降。通过部署智能光伏追踪系统，可动态调整光伏面板角度，在日照时间减少的情况下，提高单位面积发电效率，目标是提升15%-20%的日发电量。

    二、实施路径与操作细节
    1. 系统选型与部署
    目标群体：装机容量大于等于50kW的分布式光伏电站和工商业屋顶光伏系统。
    技术方案：
    （1） 双轴追踪系统：根据GPS定位和天文算法，实时调整面板朝向，确保垂直入射角度误差小于2°。
    （2） 智能控制器：集成光照强度传感器和天气预报API，在多云天气自动切换至"云层追踪模式"。
    （3） 兼容性改造：对现有固定支架系统，提供可升级的模块化追踪组件（安装时间小于4小时/10kW）。
    2. 分阶段实施计划
    （1） 评估阶段（提前10天）：
    利用GIS系统评估候选场地的遮挡情况，筛选出理论增益>18%的高价值点位。
    （2） 安装调试阶段（预测时段前5天）：
    采用"昼间发电+夜间施工"模式，减少对正常发电的影响。
    每完成5MW容量进行一次发电效率测试，对比追踪系统与固定系统的实际发电差异。
    （3） 数据反馈阶段：
    接入光伏管理平台，实时监控单瓦发电效率（要求提升大于等于15%）。
    建立异常报警机制（如角度偏差大于5°或发电效率下降大于8%时自动预警）。

    三、风险应对与保障措施
    1. 设备可靠性风险
    选用IP67防护等级的追踪设备，关键部件采用冗余设计（如双电机驱动）。
    提供5年质保服务，包含每年2次的预防性维护（含润滑、校准等）。
    2. 极端天气风险
    设置风速阈值（如大于等于12级），超过阈值时自动锁定面板至安全角度（与地面成45°）。
    配备备用电源（超级电容），确保在电网断电时仍能完成角度复位操作。

    四、长期价值与可持续性
    1. 技术迭代：可升级为AI驱动的自适应追踪系统，通过历史数据学习最优追踪策略。
    2. 成本下降：随着规模效应，预计2025年后追踪系统单瓦成本可降至0.2元/W以下。
    3. 模式复制：可推广至农业光伏、漂浮式光伏等场景，提升综合收益。

    五、决策落地建议
    1. 政策联动：申请地方政府的"光伏增效补贴"，部分地区可覆盖30%的设备成本。
    2. 金融支持：引入融资租赁模式，企业只需支付首年租金即可启动改造。
    3. 效果验证：选择1-2个典型项目进行A/B测试，对比追踪系统与固定系统的实际发电数据。

    六、综合评估
    *4*经济性：投资回收期约3-4年，比固定式系统提升15%以上的发电收益。
    *5*可持续性：纯物理改造，无额外能源消耗，生命周期长达25年。
    *3*实施难度：需解决屋顶承重加固（部分老旧建筑）和线路改造问题。
    *4*综合评级：技术成熟、收益稳定的增效方案，适合作为光伏系统升级的首选措施。

    （注：以上措施仅供参考，实际落地需结合本地电网结构、政策环境等要素进行适应性调整。）
    》
    """

    # 5. 调用大模型生成建议
    completion = client.chat.completions.create(
        model="deepseek-r1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=5000
    )
    decision = completion.choices[0].message.content.strip()

    # 6. 保存结果
    base_name = os.path.basename(os.path.splitext(original_path)[0])
    output_path = output_dir # 此处修改txt文件名
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"{'原始数据时段'}:  {comparison_general['原始数据时段']}\n")
        f.write(f"{'总太阳能辐照度峰值'}:  {comparison_general['总太阳能辐照度峰值时刻']} {comparison_general['总太阳能辐照度峰值']}\n")
        f.write(f"{'最低气温'}:  {comparison_general['最低气温时刻']} {comparison_general['最低气温']}\n")
        f.write(f"{'最高气温'}:  {comparison_general['最高气温时刻']} {comparison_general['最高气温']}\n")
        f.write(f"{'气温极差'}:  {comparison_general['气温极差']}\n")
        f.write(f"{'最低气压'}:  {comparison_general['最低气压时刻']} {comparison_general['最低气压']}\n")
        f.write(f"{'最高气压'}:  {comparison_general['最高气压时刻']} {comparison_general['最高气压']}\n")
        f.write(f"{'气压极差'}:  {comparison_general['气压极差']}\n")
        f.write(f"{'最低相对湿度'}:   {comparison_general['最低相对湿度时刻']} {comparison_general['最低相对湿度']}\n")
        f.write(f"{'最高相对湿度'}:   {comparison_general['最高相对湿度时刻']} {comparison_general['最高相对湿度']}\n")
        f.write(f"{'相对湿度极差'}:   {comparison_general['相对湿度极差']}\n")
        f.write(f"{'直射辐照度峰值'}:  {comparison_general['直射辐照度峰值时刻']} {comparison_general['直射辐照度峰值']}\n")
        f.write(f"{'峰值输出功率'}:   {comparison_general['峰值输出功率时刻']} {comparison_general['峰值输出功率']}\n")
        f.write(f"{'平均输出功率'}:   {comparison_general['平均输出功率']}\n")
        f.write("\n------\n\n")
        f.write(f"{'预测数据时段'}:   {comparison_perday['预测数据时段']}\n")
        f.write(f"{'峰值输出功率'}:   {comparison_perday['峰值输出功率时刻']} {comparison_perday['峰值输出功率']}\n")
        f.write(f"{'最高日平均功率'}:  {comparison_perday['最高日平均功率时刻']} {comparison_perday['最高日平均功率']}\n")
        f.write(f"{'最低日平均功率'}:  {comparison_perday['最低日平均功率时刻']} {comparison_perday['最低日平均功率']}\n")
        f.write(f"{'日平均功率极差'}:  {comparison_perday['日平均功率极差']}\n")
        f.write(f"{'预测日照时段'}:  {comparison_perday['预测日照时段']}\n")
        f.write(f"{'预测波动系数'}:  {comparison_perday['预测波动系数']}\n")
        f.write(f"{'阴雨天气概率'}:  {comparison_perday['阴雨天气概率']}\n")
        f.write("\n///\n\n")
        f.write(f"{'预测数据时段'}:  {comparison_perweek['预测数据时段']}\n")
        f.write(f"{'峰值输出功率'}:  {comparison_perweek['峰值输出功率时刻']} {comparison_perweek['峰值输出功率']}\n")
        f.write(f"{'最高日平均功率'}:  {comparison_perweek['最高日平均功率时刻']} {comparison_perweek['最高日平均功率']}\n")
        f.write(f"{'最低日平均功率'}:  {comparison_perweek['最低日平均功率时刻']} {comparison_perweek['最低日平均功率']}\n")
        f.write(f"{'日平均功率极差'}:  {comparison_perweek['日平均功率极差']}\n")
        f.write(f"{'预测日照时段'}:  {comparison_perweek['预测日照时段']}\n")
        f.write(f"{'预测波动系数'}:  {comparison_perweek['预测波动系数']}\n")
        f.write(f"{'阴雨天气概率'}:  {comparison_perweek['阴雨天气概率']}\n")
        f.write("\n///\n\n")
        f.write(f"{'预测数据时段'}:  {comparison_permonth['预测数据时段']}\n")
        f.write(f"{'峰值输出功率'}:  {comparison_permonth['峰值输出功率时刻']} {comparison_permonth['峰值输出功率']}\n")
        f.write(f"{'最高日平均功率'}:  {comparison_permonth['最高日平均功率时刻']} {comparison_permonth['最高日平均功率']}\n")
        f.write(f"{'最低日平均功率'}:  {comparison_permonth['最低日平均功率时刻']} {comparison_permonth['最低日平均功率']}\n")
        f.write(f"{'日平均功率极差'}:  {comparison_permonth['日平均功率极差']}\n")
        f.write(f"{'预测日照时段'}:  {comparison_permonth['预测日照时段']}\n")
        f.write(f"{'预测波动系数'}:  {comparison_permonth['预测波动系数']}\n")
        f.write(f"{'阴雨天气概率'}:  {comparison_permonth['阴雨天气概率']}\n")
        f.write("\n///\n\n")
        f.write(f"{'预测数据时段'}:  {comparison['预测数据时段']}\n")
        f.write(f"{'峰值输出功率'}:  {comparison['峰值输出功率时刻']} {comparison['峰值输出功率']}\n")
        f.write(f"{'最高日平均功率'}:  {comparison['最高日平均功率时刻']} {comparison['最高日平均功率']}\n")
        f.write(f"{'最低日平均功率'}:  {comparison['最低日平均功率时刻']} {comparison['最低日平均功率']}\n")
        f.write(f"{'日平均功率极差'}:  {comparison['日平均功率极差']}\n")
        f.write(f"{'预测日照时段'}:  {comparison['预测日照时段']}\n")
        f.write(f"{'预测波动系数'}:  {comparison['预测波动系数']}\n")
        f.write(f"{'阴雨天气概率'}:  {comparison['阴雨天气概率']}\n")
        f.write("\n------\n\n")
        f.write(decision)
    print(f"结果已保存至 {output_path}")


if __name__ == "__main__":
    original_csv = 'solar/original_data/solar1.csv' # 此处修改原始数据地址
    forecast_csv = 'solar/forecast_data/solar2.csv' # 此处修改预测数据地址
    txt_dir = 'solar/txt' # 此处修改txt文件目录
    analyze_combine_data_solar(original_csv, forecast_csv,txt_dir)