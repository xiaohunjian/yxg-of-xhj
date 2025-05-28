package com.yxg.history.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DecisionData {
    String dimension;
    String basis;
    String stars;
}//返回决策推荐指数的表格数据
