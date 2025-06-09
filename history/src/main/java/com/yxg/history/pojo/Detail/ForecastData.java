package com.yxg.history.pojo.Detail;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

//用于存放DetailReturn的预测数据
@Data
@AllArgsConstructor
@NoArgsConstructor
public class ForecastData{
    public List<DetailMap> day;
    public List<DetailMap> week;
    public List<DetailMap> month;
    public List<DetailMap> quarter;
}
