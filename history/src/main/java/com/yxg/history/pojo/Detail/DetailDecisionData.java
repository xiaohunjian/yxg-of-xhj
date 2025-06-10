package com.yxg.history.pojo.Detail;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
//决策数据
@Data
@AllArgsConstructor
@NoArgsConstructor
public class DetailDecisionData{
    public DetailDecision first;
    public DetailDecision second;
    public DetailDecision third;
}
