package com.yxg.history.pojo.Detail;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

//返回所有信息
@AllArgsConstructor
@Data
@NoArgsConstructor
public class DetailReturn {
    //用户预测的原始数据
    public List<DetailMap> originalData;
    //预测信息
    public ForecastData forecastData;
    //决策信息
    public DetailDecisionData decisionData;
    //饼状图信息
    public Object pieChart;
    //线型图信息
    public Object lineChart;
    //星级信息
    public StarData starData;
 }

