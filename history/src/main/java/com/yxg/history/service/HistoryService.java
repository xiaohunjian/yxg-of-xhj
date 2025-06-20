package com.yxg.history.service;

import com.yxg.history.pojo.Result;

import java.io.IOException;
import java.time.LocalDateTime;

public interface HistoryService {
    Result hist(int id);

    Result reHist(String time, String type) throws IOException;
}
