package com.yxg.history.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class History {
    private int id;
    private String time;
    private String addr;
    private String type;
    private String fileName;
}//历史记录
