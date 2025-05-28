package com.yxg.history.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class ReHistRequest {
    private String time;
    private String type;
}//获取详细历史记录请求体
