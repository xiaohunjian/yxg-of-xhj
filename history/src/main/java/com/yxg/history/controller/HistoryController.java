package com.yxg.history.controller;

import com.yxg.history.pojo.History;
import com.yxg.history.pojo.ReHistRequest;
import com.yxg.history.pojo.Result;
import com.yxg.history.service.HistoryService;
import javax.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.time.LocalDateTime;

@Component

@RestController
public class HistoryController {

    @Autowired
    private HistoryService historyService;

    @GetMapping("/hist/{page}")
    public Result hist(HttpServletRequest request,@PathVariable int page){
        int id = (int) request.getAttribute("id");
        return historyService.hist(id,page-1);
    }

    @PostMapping("/reHist")
    public Result reHist(@RequestBody ReHistRequest reHistRequest){
        try{
            return historyService.reHist(reHistRequest.getTime(),reHistRequest.getType());
        }
        catch (IOException e){
            e.printStackTrace();
            return new Result(400,"fail",null);
        }
    }

    @GetMapping("/get")
    public Result get(){
        return new Result(200,"success",null);
    }
}
