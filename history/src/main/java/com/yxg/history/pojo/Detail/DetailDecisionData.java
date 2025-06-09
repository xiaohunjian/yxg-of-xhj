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
    public List<DetailDecision> first;
    public List<DetailDecision> second;
    public List<DetailDecision> third;
}
