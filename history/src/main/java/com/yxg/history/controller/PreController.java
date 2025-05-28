package com.yxg.history.controller;

import com.yxg.history.pojo.AdvRequest;
import com.yxg.history.pojo.PreRequest;
import com.yxg.history.pojo.Result;
import com.yxg.history.service.PreService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import javax.servlet.http.HttpServletRequest;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Component
@RestController
public class PreController {

    @Autowired
    private PreService preService;

    @PostMapping("/prediction")
    public Result prediction(@RequestBody PreRequest preRequest, HttpServletRequest request) {
        String name = request.getAttribute("name").toString();
        String time;
        Path uploadPath;
        MultipartFile file = preRequest.getFile();
        try {
            String basePath = "C:\\Users\\yijian\\Desktop\\project\\yxg\\user";
            LocalDateTime now = LocalDateTime.now();
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH-mm");
            time = now.format(formatter);
            uploadPath = Paths.get(basePath, name, now.format(formatter));
            Files.createDirectories(uploadPath);
            Path filePath = uploadPath.resolve("pre.csv");
            file.transferTo(filePath);
        } catch (IOException e) {
            e.printStackTrace();
            return new Result(400, "error", null);
        }
        return preService.prediction(time, name, uploadPath,preRequest.getPreRequestLow().getType(),preRequest.getPreRequestLow().getFileName());
    }

    @PostMapping("/getAdv")
    public Result getAdv(@RequestBody AdvRequest advRequest, HttpServletRequest request) {
        String name = request.getAttribute("name").toString();
        int id = (int) request.getAttribute("id");
        try{
            return preService.getAdv(id,advRequest.getTime(),advRequest.getTimes(),name);
        }catch (Exception e){
            e.printStackTrace();
            return new Result(400, "error", null);
        }
    }
}
