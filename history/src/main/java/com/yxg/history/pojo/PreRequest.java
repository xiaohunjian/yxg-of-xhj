package com.yxg.history.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.web.multipart.MultipartFile;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class PreRequest {
    private PreRequestLow data;
    private MultipartFile file;
}//预测请求体
