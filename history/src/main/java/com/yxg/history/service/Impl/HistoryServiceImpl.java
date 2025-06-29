package com.yxg.history.service.Impl;


import com.alibaba.fastjson.JSON;
import com.yxg.history.mapper.HistoryMapper;
import com.yxg.history.pojo.*;
import com.yxg.history.pojo.Detail.*;
import com.yxg.history.service.HistoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

@Service
public class HistoryServiceImpl implements HistoryService {
    @Autowired
    private HistoryMapper historyMapper;

    @Override
    public Result hist(int id) {
        List<History> hist = historyMapper.selectByPage(id);
        List<HistoryPre> historyPre = new ArrayList<>();
        for (History history : hist) {
            historyPre.add(new HistoryPre(history.getTime(),history.getType(),history.getFileName()));
        }

        return new Result(200,"success",historyPre);
    }

    @Override
    public Result reHist(String time, String type) throws IOException{
        History history = historyMapper.selectByTime(time,type);
        String path = history.getAddr()+"\\res.txt";
        BufferedReader br = new BufferedReader(new FileReader(path));
        StringBuffer sb = new StringBuffer();
        String line = null;
        while ((line = br.readLine()) != null) {
            sb.append(line);
            sb.append("\n");
        }
        String res = sb.toString();
        String[] list = res.split("------");
        DetailReturn dr = new DetailReturn();
        dr.setOriginalData(dataHandle(list[0]));
        dr.setForecastData(forHandle(list[1]));
        dr.setDecisionData(decisionHandle(list[2]));
        String json = new String(Files.readAllBytes(Paths.get(history.getAddr()+"\\bar.json")));
        CharJson data = JSON.parseObject(json, CharJson.class);
        ChartData chartData = data.getData();
        dr.setPieChart(chartData.getPieChart());
        dr.setLineChart(chartData.getLineChart());
        dr.setStarData(starHandle(list[2]));
        return new Result(200,"success",dr);
    }

    //处理文本数据方法
    public List<DetailMap> dataHandle(String string){
        List<DetailMap> list = new ArrayList<>();
        String[] strings = string.split("\n");
        for(String str:strings){
            if("".equals(str)){
                continue;
            }
            list.add(new DetailMap(str.split(":  ")[0],str.split(":  ")[1]));
        }
        return list;
    }

    public ForecastData forHandle(String string){
        ForecastData fd = new ForecastData();
        String[] strings = string.split("///");
        fd.day = dataHandle(strings[0]);
        fd.week = dataHandle(strings[1]);
        fd.month = dataHandle(strings[2]);
        fd.quarter = dataHandle(strings[3]);
        return fd;
    }
    //处理决策数据方法
    public DetailDecisionData decisionHandle (String string){
        DetailDecisionData ddd = new DetailDecisionData();
        String[] strings = string.split("///");
        ddd.first = decisionHandleLow(strings[0]);
        ddd.second = decisionHandleLow(strings[1]);
        ddd.third = decisionHandleLow(strings[2]);
        return ddd;
    }
    //处理单种决策建议
    public DetailDecision decisionHandleLow(String string){
        DetailDecision dd = new DetailDecision();
        String[] strs = string.split("\n");
        dd.setTitle(strs[2]);
        String[] strs1 = string.split("\n\n");
        List<Section> sections = new ArrayList<>();
        for(int i = 1;i<strs1.length-2;i++){
            String head;
            String[] str2 = strs1[i].split("\n");
            head = str2[(i==1)?1:0];
            StringBuffer sb = new StringBuffer();
            for(int j = (i==1)?2:1;j<str2.length;j++){
                sb.append(str2[j]);
                sb.append("\n");
            }
            sections.add(new Section(head,sb.toString()));
        }
        dd.setSections(sections);
        return dd;
    }
    //处理星级数据
    public StarData starHandle(String string){
        StarData sd = new StarData();
        String[] strings = string.split("///");
        sd.setFirst(starHandleLow(strings[0]));
        sd.setSecond(starHandleLow(strings[1]));
        sd.setThird(starHandleLow(strings[2]));
        return sd;
    }
    //处理单个建议中星级
    public List<DetailStar> starHandleLow(String string){
        List<DetailStar> list = new ArrayList<>();
        String[] strings = string.split("\n");
        int i = 0;
        while(!strings[i].contains("六、综合评估")){
            i++;
        }
        for(int j = i+1;j<=i+4;j++){
            DetailStar ds = new DetailStar();
            String string1 = strings[j];
            ds.setScore(string1.toCharArray()[1]-'0');
            String[] strings1 = string1.split("：");
            ds.setBasis(strings1[1]);
            ds.setDimension(strings1[0].split("\\*")[2]);
            list.add(ds);
        }
        return list;
    }
}
