package com.yxg.history.service.Impl;

import com.yxg.history.mapper.PreMapper;
import com.yxg.history.pojo.History;
import com.yxg.history.pojo.Result;
import com.yxg.history.service.HistoryService;
import com.yxg.history.service.PreService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.io.IOException;
import java.nio.file.Path;

@Service
public class PreServiceImpl implements PreService {
    @Autowired
    private PreMapper preMapper;

    @Autowired
    private HistoryService historyService;

    @Override
    public Result prediction(String time, String name, Path uploadPath, String type,String filename) throws IOException {
        String add = "C:\\Users\\yijian\\Desktop\\project\\yxg\\user\\"+name+"\\"+time;
        int id = preMapper.findByName(name);
        History history = new History(id,time,add,type,filename);
        RestTemplate restTemplate = new RestTemplate();;
        String url = "http://localhost:5000/predict";
        String requestBody = "{\"address\":[\""+
                add+"\\pre.csv\""+",\""+
                add+"\\bar.json\""+",\""+
                add+"\\res.txt\"]," +"\n"+
                "\"category\":"+"\""+type+"\""+"}";
        requestBody = requestBody.replace("\\","\\\\");
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<String > requestEntity = new HttpEntity<>(requestBody,headers);
        try{
            ResponseEntity<Result> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    requestEntity,
                    Result.class
            );
        }catch (Exception e){
            e.printStackTrace();
            return new Result(400,"fail",null);
        }
        //此处调用接口进行分析，存储文件并返回结果
        preMapper.addFile(history);
        return historyService.reHist(time,type);
    }
}
