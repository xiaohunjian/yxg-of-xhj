package com.yxg.history.service.Impl;


import com.yxg.history.mapper.HistoryMapper;
import com.yxg.history.pojo.History;
import com.yxg.history.pojo.HistoryPre;
import com.yxg.history.pojo.Result;
import com.yxg.history.service.HistoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Service
public class HistoryServiceImpl implements HistoryService {
    @Autowired
    private HistoryMapper historyMapper;

    @Override
    public Result hist(int id,int page) {
        List<History> hist = historyMapper.selectByPage(id,page);
        List<HistoryPre> historyPre = new ArrayList<>();
        for (History history : hist) {
            historyPre.add(new HistoryPre(history.getTime(),history.getType(),history.getFileName()));
        }
        return new Result(200,"success",historyPre);
    }

    @Override
    public Result reHist(String time, String type) throws IOException{
        History history = historyMapper.selectByTime(time,type);
        List<List<String>> datas = new ArrayList<>();
        readFile(history,datas,"\\pre.csv");
        readFile(history,datas,"\\res.txt");
        return new Result(200,"success",datas);
    }

    void readFile(History history,List<List<String>> datas, String path) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(history.getAddr()+path));
            List<String> strings = new ArrayList<>();
            String line;
            StringBuilder sb = new StringBuilder();
            while ((line = br.readLine()) != null) {
                strings.add(line);
            }
            datas.add(strings);
            br.close();
    }
}
