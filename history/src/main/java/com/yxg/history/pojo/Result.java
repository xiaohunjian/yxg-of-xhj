package com.yxg.history.pojo;

import javax.servlet.annotation.WebFilter;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class Result {
    private int code;
    private String msg;
    private Object data;
}
