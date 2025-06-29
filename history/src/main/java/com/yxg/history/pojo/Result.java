package com.yxg.history.pojo;

import javax.servlet.annotation.WebFilter;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Result {
    private int code;
    private String message;
    private Object data;
}
