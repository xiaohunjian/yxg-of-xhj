package com.yxg.history.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.xml.soap.Detail;
import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class HisReturn {
    private String content;
    private List<DecisionData> decisionData;

}//决策数据返回
