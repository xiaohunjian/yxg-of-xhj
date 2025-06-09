package com.yxg.history.service.Impl;

import com.yxg.history.mapper.PreMapper;
import com.yxg.history.pojo.DecisionData;
import com.yxg.history.pojo.HisReturn;
import com.yxg.history.pojo.History;
import com.yxg.history.pojo.Result;
import com.yxg.history.service.PreService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

@Service
public class PreServiceImpl implements PreService {
    @Autowired
    private PreMapper preMapper;

    @Override
    public Result prediction(String time, String name, Path uploadPath, String type,String filename) {
        String add = "C:\\Users\\yijian\\Desktop\\project\\yxg\\user\\"+name+"\\"+time;
        int id = preMapper.findByName(name);
        History history = new History(id,time,add,type,filename);
        preMapper.addFile(history);
        //此处调用接口进行分析，存储文件并返回结果
        return null;
    }

    @Override
    public Result getAdv(int id, String time,int times,String name) throws IOException {
        String add = preMapper.getFile(id,time);
        BufferedReader br = new BufferedReader(new FileReader("C:\\Users\\yijian\\Desktop\\project\\yxg\\user\\"+name+"\\"+time+"\\adv.txt"));
        String line;
        StringBuilder sb = new StringBuilder();//建议
        List<String> list = new ArrayList<>();//星级对应词条
        List<String> stars = new ArrayList<>();//星级
        List<String> list1 = new ArrayList<>();//评分依据
        line = br.readLine();
        while ((line = br.readLine()) != null) {
            if(line.contains("*")){
                char[] chars = line.toCharArray();
                stars.add(String.valueOf(chars[1]));
                StringBuilder sb1 = new StringBuilder();
                for(int i = 3; i < chars.length; i++){
                    sb1.append(String.valueOf(chars[i]));
                }
                String s = sb1.toString();
                String[] split = s.split("：");
                list.add(split[0]);
                list1.add(split[1]);

            }else if(line.contains("///")){
                sb.append(line);
                sb.append("\n");
            }else{
                sb.append(line);
                sb.append("\n");
            }
        }
        br.close();
        String[] s = sb.toString().split("///");
        int[] p = new int[4];
        Arrays.fill(p,list.size()-1);
        p[0] = 0;
        int a = 1;
        for(int i=0;i<list.size();i++){
            if(list.get(i).contains("///")){
                p[a] = i;
                a++;
            }
        }
        List<DecisionData> data = new ArrayList<>();
        for(int i = (list.size()/3)*(times-1);i<(list.size()/3)*times;i++){
            data.add(new DecisionData(list.get(i),list1.get(i),stars.get(i)));
        }
        HisReturn hisReturn = new HisReturn(s[times-1],data);
        return new Result(200,"success",hisReturn);
    }
}
