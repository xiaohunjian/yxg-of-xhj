package com.yxg.history.pojo.Detail;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

//存放DetailReturn中决策信息
@AllArgsConstructor
@Data
@NoArgsConstructor
public class DetailDecision{
    private String title;
    private List<Section> sections;
}
