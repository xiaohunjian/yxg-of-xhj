package com.yxg.login.controller;

import com.yxg.login.pojo.LoginReq;
import com.yxg.login.pojo.Result;
import com.yxg.login.pojo.User;
import com.yxg.login.service.LoginService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@Component

@RestController
public class LoginController {
    @Value("${jwt.key}")
    private String key;

    @Autowired
    private LoginService loginService;

    @PostMapping("/login")
    public Result login(@RequestBody LoginReq loginReq) {
        return loginService.login(loginReq);
    }

    @PostMapping("/register")
    public  Result register(@RequestBody User user){
        return loginService.register(user);
    }
}
