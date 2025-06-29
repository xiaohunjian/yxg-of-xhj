package com.yxg.history.controller;

import com.yxg.history.pojo.PreRequest;
import com.yxg.history.pojo.PreRequestLow;
import com.yxg.history.pojo.Result;
import com.yxg.history.service.PreService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.*;
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
    public Result prediction(HttpServletRequest request,@ModelAttribute PreRequest preRequest) throws IOException {
        String name = request.getAttribute("name").toString();
        String time;
        MultipartFile file = preRequest.getFile();
        String fileName = preRequest.getData().getFileName();
        String type = preRequest.getData().getType();
        Path uploadPath;
        try {
            String basePath = "C:\\Users\\yijian\\Desktop\\project\\yxg\\user";
            LocalDateTime now = LocalDateTime.now();
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH-mm");
            time = now.format(formatter);
            uploadPath = Paths.get(basePath, name, now.format(formatter));
            Files.createDirectories(uploadPath);
            Path filePath = uploadPath.resolve("pre.csv");
            file.transferTo(filePath);
            return preService.prediction(time, name, uploadPath,type,fileName);
        } catch (IOException e) {
            e.printStackTrace();
            return new Result(400, "error", null);
        }
    }
}
